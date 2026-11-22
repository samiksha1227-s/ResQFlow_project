import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/emergency_provider.dart';
import '../../theme/app_theme.dart';
import '../../models/models.dart';

class ControlRoomDashboard extends StatelessWidget {
  const ControlRoomDashboard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<EmergencyProvider>(
      builder: (context, provider, _) {
        return Row(
          children: [
            // Left Panel - Operations & Incident List
            Expanded(
              flex: 1,
              child: Container(
                decoration: const BoxDecoration(
                  border: Border(right: BorderSide(color: AppTheme.divider)),
                ),
                child: Column(
                  children: [
                    _buildStatsGrid(provider),
                    const Divider(),
                    Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: ElevatedButton.icon(
                        onPressed: () => provider.simulateAccident(),
                        icon: const Icon(Icons.warning),
                        label: const Text('SIMULATE ACCIDENT'),
                        style: ElevatedButton.styleFrom(
                          minimumSize: const Size(double.infinity, 50),
                        ),
                      ),
                    ),
                    Expanded(child: _buildIncidentList(provider)),
                  ],
                ),
              ),
            ),
            
            // Middle Panel - Active Incident Details & Map placeholder
            Expanded(
              flex: 2,
              child: _buildIncidentDetails(context, provider),
            ),
            
            // Right Panel - Timeline & Communication Logs
            Expanded(
              flex: 1,
              child: Container(
                decoration: const BoxDecoration(
                  border: Border(left: BorderSide(color: AppTheme.divider)),
                ),
                child: _buildTimelineAndLogs(provider),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildStatsGrid(EmergencyProvider provider) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          Row(
            children: [
              _StatBox(title: 'ACTIVE\nINCIDENTS', value: '${provider.activeIncidents}', color: AppTheme.infoBlueLight),
              const SizedBox(width: 8),
              _StatBox(title: 'CRITICAL\nINCIDENTS', value: '${provider.criticalIncidents}', color: AppTheme.criticalPulse),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              _StatBox(title: 'AMBULANCES\nAVAILABLE', value: '${provider.ambulancesAvailable}', color: AppTheme.successGreenLight),
              const SizedBox(width: 8),
              _StatBox(title: 'HOSPITALS\nREADY', value: '${provider.hospitalsReady}', color: AppTheme.successGreenLight),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildIncidentList(EmergencyProvider provider) {
    if (provider.currentIncident == null && provider.sourceReports.isEmpty) {
      return const Center(child: Text('No active incidents', style: TextStyle(color: AppTheme.textMuted)));
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (provider.sourceReports.isNotEmpty && provider.currentIncident == null)
          Card(
            child: ListTile(
              title: const Text('4 NEW REPORTS RECEIVED'),
              subtitle: const Text('Pending AI Fusion...'),
              trailing: ElevatedButton(
                onPressed: () => provider.runIncidentFusion(),
                child: const Text('FUSE REPORTS'),
              ),
            ),
          ),
        if (provider.currentIncident != null)
          Card(
            color: AppTheme.darkCardLight,
            shape: RoundedRectangleBorder(
              side: BorderSide(
                color: AppTheme.severityColor(provider.currentIncident!.severity ?? 'INFO'),
                width: 2,
              ),
              borderRadius: BorderRadius.circular(8),
            ),
            child: ListTile(
              title: Text('Incident ${provider.currentIncident!.incidentId}',
                  style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text('Status: ${provider.currentIncident!.status}'),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
            ),
          )
      ],
    );
  }

  Widget _buildIncidentDetails(BuildContext context, EmergencyProvider provider) {
    final incident = provider.currentIncident;
    if (incident == null) {
      return const Center(
        child: Text(
          'Select an incident to view details\n\nOr click SIMULATE ACCIDENT to begin',
          textAlign: TextAlign.center,
          style: TextStyle(color: AppTheme.textMuted, fontSize: 18),
        ),
      );
    }

    return ListView(
      padding: const EdgeInsets.all(24),
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Incident ${incident.incidentId}', style: Theme.of(context).textTheme.headlineLarge),
            Chip(
              label: Text(incident.status, style: const TextStyle(fontWeight: FontWeight.bold)),
              backgroundColor: AppTheme.statusColor(incident.status),
            ),
          ],
        ),
        const SizedBox(height: 16),
        
        // AI Fusion Info
        _buildInfoCard(
          'Multi-Source AI Fusion',
          '${incident.reports.length} duplicate reports merged into ONE verified incident.',
          Icons.merge_type,
          action: incident.status == 'FUSED' ? ElevatedButton(
            onPressed: () => provider.verifyIncident(),
            child: const Text('VERIFY INCIDENT'),
          ) : null,
        ),
        
        // Victim Info
        if (incident.status != 'FUSED' && incident.status != 'DETECTED')
          _buildInfoCard(
            'Victim Information',
            incident.victims == null ? 'Pending assessment...' : 
              '${incident.victims!.totalCount} Victims | ${incident.victims!.unconsciousCount} Unconscious\nHeavy Bleeding: ${incident.victims!.hasHeavyBleeding ? "YES" : "NO"}',
            Icons.people,
            action: incident.victims == null ? ElevatedButton(
              onPressed: () => provider.addVictimData(Victim(
                totalCount: 3,
                unconsciousCount: 1,
                hasHeavyBleeding: true,
                hasBreathingDifficulty: true,
                hasCriticalCondition: false,
                hasVisibleInjury: true,
                hasElderly: false,
                hasChild: false,
              )),
              child: const Text('ADD DEMO VICTIMS'),
            ) : null,
          ),
          
        // Severity
        if (incident.victims != null)
          _buildInfoCard(
            'Severity Assessment',
            incident.severity == null ? 'Pending AI assessment...' : incident.severity!,
            Icons.warning_amber_rounded,
            color: incident.severity != null ? AppTheme.severityColor(incident.severity!) : null,
            action: incident.severity == null ? ElevatedButton(
              onPressed: () => provider.runSeverityAssessment(),
              child: const Text('ASSESS SEVERITY'),
            ) : null,
          ),
          
        // Requirements
        if (incident.severity != null)
          _buildInfoCard(
            'Emergency Requirements',
            incident.requirements.isEmpty ? 'Pending requirement prediction...' : 
              incident.requirements.map((r) => '• ${r.resource} (x${r.quantity})').join('\n'),
            Icons.local_hospital,
            action: incident.requirements.isEmpty ? ElevatedButton(
              onPressed: () => provider.predictRequirements(),
              child: const Text('PREDICT REQUIREMENTS'),
            ) : null,
          ),
          
        // Ambulance
        if (incident.requirements.isNotEmpty)
          _buildInfoCard(
            'Ambulance Dispatch',
            incident.assignedAmbulance == null ? 'Pending match...' : 
              'Selected: ${incident.assignedAmbulance!.name}\nDistance: ${incident.assignedAmbulance!.distanceKm} km',
            Icons.directions_car,
            action: incident.assignedAmbulance == null ? ElevatedButton(
              onPressed: () => provider.matchAmbulance(),
              child: const Text('MATCH AMBULANCE'),
            ) : (incident.status == 'AMBULANCE_MATCHED' ? ElevatedButton(
              onPressed: () => provider.sendAmbulanceAlert(),
              child: const Text('SEND DISPATCH (LoRa)'),
            ) : null),
          ),
          
        // Routing / Road Block Simulation
        if (incident.currentRoute != null)
          _buildInfoCard(
            'Offline Routing',
            'Route: ${incident.currentRoute!.name}\nETA: ${incident.currentRoute!.etaMinutes} mins\nPath: ${incident.currentRoute!.roads.join(" → ")}',
            Icons.map,
            color: incident.currentRoute!.isBlocked ? AppTheme.emergencyOrange : null,
            action: !incident.currentRoute!.isBlocked && incident.status == 'ROUTE_ACTIVE' ? ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: AppTheme.emergencyOrange),
              onPressed: () => provider.simulateRoadBlock(),
              child: const Text('SIMULATE ROAD BLOCK'),
            ) : null,
          ),
          
        // Hospital Matching
        if (incident.ambulanceStatus == 'AT_HOSPITAL' || incident.ambulanceStatus == 'EN_ROUTE_TO_HOSPITAL' || incident.ambulanceStatus == 'PICKED_UP' || incident.ambulanceStatus == 'ARRIVED')
           _buildInfoCard(
            'Hospital Assignment',
            incident.assignedHospital == null ? 'Pending match...' : 
              'Selected: ${incident.assignedHospital!.name}\nStatus: ${incident.assignedHospital!.status}',
            Icons.business,
            action: incident.assignedHospital == null ? ElevatedButton(
              onPressed: () => provider.matchHospital(),
              child: const Text('MATCH HOSPITAL'),
            ) : (incident.status == 'HOSPITAL_MATCHED' ? ElevatedButton(
              onPressed: () => provider.sendHospitalAlert(),
              child: const Text('SEND ALERT (LoRa)'),
            ) : null),
          ),
          
        // Close Incident
        if (incident.status == 'HANDOVER')
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 16.0),
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: AppTheme.successGreen),
              onPressed: () => provider.closeIncident(),
              child: const Text('CLOSE INCIDENT'),
            ),
          )
      ],
    );
  }

  Widget _buildInfoCard(String title, String content, IconData icon, {Widget? action, Color? color}) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color ?? AppTheme.textSecondary),
                const SizedBox(width: 8),
                Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              ],
            ),
            const SizedBox(height: 12),
            Text(content, style: TextStyle(fontSize: 16, color: color ?? AppTheme.textPrimary)),
            if (action != null) ...[
              const SizedBox(height: 16),
              action,
            ]
          ],
        ),
      ),
    );
  }

  Widget _buildTimelineAndLogs(EmergencyProvider provider) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          width: double.infinity,
          color: AppTheme.darkCardLight,
          child: const Text('INCIDENT TIMELINE', style: TextStyle(fontWeight: FontWeight.bold)),
        ),
        Expanded(
          flex: 3,
          child: provider.currentIncident == null ? const Center(child: Text('No timeline data')) :
          ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: provider.currentIncident!.timeline.length,
            itemBuilder: (context, index) {
              final event = provider.currentIncident!.timeline[index];
              return Padding(
                padding: const EdgeInsets.only(bottom: 16.0),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Column(
                      children: [
                        Icon(Icons.circle, size: 12, color: AppTheme.statusColor(event.status)),
                        if (index < provider.currentIncident!.timeline.length - 1)
                          Container(width: 2, height: 40, color: AppTheme.divider),
                      ],
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(event.event, style: const TextStyle(fontWeight: FontWeight.bold)),
                          if (event.details != null)
                            Text(event.details!, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
                          Text(
                            '${event.timestamp.hour}:${event.timestamp.minute.toString().padLeft(2, '0')}:${event.timestamp.second.toString().padLeft(2, '0')}', 
                            style: const TextStyle(color: AppTheme.textMuted, fontSize: 10)
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ),
        Container(
          padding: const EdgeInsets.all(16),
          width: double.infinity,
          color: AppTheme.darkCardLight,
          child: const Text('LoRa COMMUNICATION LOGS', style: TextStyle(fontWeight: FontWeight.bold)),
        ),
        Expanded(
          flex: 2,
          child: ListView.builder(
            padding: const EdgeInsets.all(12),
            itemCount: provider.communicationLog.length,
            itemBuilder: (context, index) {
              final log = provider.communicationLog[provider.communicationLog.length - 1 - index];
              return Padding(
                padding: const EdgeInsets.only(bottom: 8.0),
                child: Text(
                  '${log['time']} [${log['event']}]\n${log['details']}',
                  style: const TextStyle(fontFamily: 'monospace', fontSize: 11, color: AppTheme.successGreenLight),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}

class _StatBox extends StatelessWidget {
  final String title;
  final String value;
  final Color color;

  const _StatBox({required this.title, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppTheme.darkCardLight,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(value, style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: color)),
            Text(title, style: const TextStyle(fontSize: 10, color: AppTheme.textSecondary)),
          ],
        ),
      ),
    );
  }
}
