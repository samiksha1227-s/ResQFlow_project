import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/emergency_provider.dart';
import '../../theme/app_theme.dart';

class HospitalDashboard extends StatelessWidget {
  const HospitalDashboard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<EmergencyProvider>(
      builder: (context, provider, _) {
        final incident = provider.currentIncident;
        final isAssigned = incident != null && incident.assignedHospital?.id == 'H01';
        
        if (!isAssigned || incident.status == 'CLOSED') {
          return const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.local_hospital, size: 64, color: AppTheme.textMuted),
                SizedBox(height: 16),
                Text('NORMAL OPERATIONS', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppTheme.textMuted)),
                Text('No incoming emergencies.', style: TextStyle(color: AppTheme.textSecondary)),
              ],
            ),
          );
        }

        return Row(
          children: [
            Expanded(
              flex: 1,
              child: Container(
                decoration: const BoxDecoration(
                  border: Border(right: BorderSide(color: AppTheme.divider)),
                ),
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.warning, color: AppTheme.emergencyRed),
                        SizedBox(width: 8),
                        Text('INCOMING EMERGENCY', style: TextStyle(color: AppTheme.emergencyRed, fontWeight: FontWeight.bold, fontSize: 18)),
                      ],
                    ),
                    const SizedBox(height: 24),
                    _buildDetail('Incident ID', incident.incidentId),
                    _buildDetail('Severity', incident.severity ?? 'UNKNOWN', color: AppTheme.severityColor(incident.severity ?? 'LOW')),
                    _buildDetail('Victims', '${incident.victims?.totalCount ?? "?"}'),
                    _buildDetail('Ambulance', incident.assignedAmbulance?.id ?? 'UNKNOWN'),
                    _buildDetail('Patient Status', 
                      'Unconscious: ${incident.victims?.unconsciousCount ?? 0}\n'
                      'Bleeding: ${incident.victims?.hasHeavyBleeding == true ? "YES" : "NO"}\n'
                      'Breathing Diff: ${incident.victims?.hasBreathingDifficulty == true ? "YES" : "NO"}'
                    ),
                  ],
                ),
              ),
            ),
            Expanded(
              flex: 2,
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Text('HOSPITAL PREPARATION CHECKLIST', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 16),
                    if (incident.hospitalReady)
                      Container(
                        padding: const EdgeInsets.all(16),
                        margin: const EdgeInsets.bottom(16),
                        decoration: BoxDecoration(
                          color: AppTheme.successGreen.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: AppTheme.successGreen),
                        ),
                        child: const Row(
                          children: [
                            Icon(Icons.check_circle, color: AppTheme.successGreen),
                            SizedBox(width: 16),
                            Text('HOSPITAL READY FOR PATIENT ARRIVAL', style: TextStyle(color: AppTheme.successGreen, fontWeight: FontWeight.bold, fontSize: 16)),
                          ],
                        ),
                      ),
                    Expanded(
                      child: ListView.builder(
                        itemCount: incident.requirements.length,
                        itemBuilder: (context, index) {
                          final req = incident.requirements[index];
                          return Card(
                            margin: const EdgeInsets.only(bottom: 8),
                            color: req.isReady ? AppTheme.successGreen.withOpacity(0.1) : AppTheme.darkCardLight,
                            child: ListTile(
                              leading: Icon(
                                req.isReady ? Icons.check_circle : Icons.radio_button_unchecked,
                                color: req.isReady ? AppTheme.successGreen : AppTheme.textMuted,
                              ),
                              title: Text('${req.resource} (x${req.quantity})'),
                              subtitle: Text('Priority: ${req.priority}'),
                              trailing: req.isReady ? const Text('READY', style: TextStyle(color: AppTheme.successGreen, fontWeight: FontWeight.bold))
                                : ElevatedButton(
                                  onPressed: () => provider.markRequirementReady(index),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: AppTheme.infoBlue,
                                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                  ),
                                  child: const Text('MARK READY'),
                                ),
                            ),
                          );
                        },
                      ),
                    ),
                    if (!incident.hospitalReady)
                      ElevatedButton(
                        onPressed: () => provider.markAllRequirementsReady(),
                        style: ElevatedButton.styleFrom(backgroundColor: AppTheme.successGreen, padding: const EdgeInsets.symmetric(vertical: 20)),
                        child: const Text('MARK ALL READY', style: TextStyle(fontSize: 18)),
                      ),
                    if (incident.hospitalReady && incident.status != 'HANDOVER')
                      ElevatedButton(
                        onPressed: () => provider.completeHandover(),
                        style: ElevatedButton.styleFrom(backgroundColor: AppTheme.infoBlue, padding: const EdgeInsets.symmetric(vertical: 20)),
                        child: const Text('COMPLETE PATIENT HANDOVER', style: TextStyle(fontSize: 18)),
                      ),
                    if (incident.status == 'HANDOVER')
                      const Center(child: Text('PATIENT HANDED OVER. INCIDENT RESOLVED.', style: TextStyle(color: AppTheme.successGreen, fontSize: 18, fontWeight: FontWeight.bold))),
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildDetail(String label, String value, {Color? color}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 14)),
          const SizedBox(height: 4),
          Text(value, style: TextStyle(color: color ?? AppTheme.textPrimary, fontSize: 18, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
