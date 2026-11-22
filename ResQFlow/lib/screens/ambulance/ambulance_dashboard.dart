import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/emergency_provider.dart';
import '../../theme/app_theme.dart';

class AmbulanceDashboard extends StatelessWidget {
  const AmbulanceDashboard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<EmergencyProvider>(
      builder: (context, provider, _) {
        final incident = provider.currentIncident;
        final isAssigned = incident != null && incident.assignedAmbulance?.id == 'A01';
        
        if (!isAssigned || incident.status == 'CLOSED' || incident.status == 'HANDOVER') {
          return const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.check_circle_outline, size: 64, color: AppTheme.successGreen),
                SizedBox(height: 16),
                Text('AVAILABLE', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppTheme.successGreen)),
                Text('Waiting for dispatch...', style: TextStyle(color: AppTheme.textSecondary)),
              ],
            ),
          );
        }

        return Row(
          children: [
            Expanded(
              flex: 2,
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Text('EMERGENCY DISPATCH', style: TextStyle(color: AppTheme.emergencyRed, fontWeight: FontWeight.bold, fontSize: 18)),
                    const SizedBox(height: 16),
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Incident: ${incident.incidentId}', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                            const SizedBox(height: 16),
                            _buildInfoRow('Severity:', incident.severity ?? 'UNKNOWN', AppTheme.severityColor(incident.severity ?? 'LOW')),
                            _buildInfoRow('Victims:', '${incident.victims?.totalCount ?? "?"}', Colors.white),
                            _buildInfoRow('Location:', '${incident.latitude.toStringAsFixed(4)}, ${incident.longitude.toStringAsFixed(4)}', Colors.white),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    
                    if (incident.ambulanceStatus == null)
                      ElevatedButton(
                        onPressed: () => provider.acceptEmergency(),
                        style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 20)),
                        child: const Text('ACCEPT DISPATCH & START ROUTE', style: TextStyle(fontSize: 18)),
                      )
                    else if (incident.ambulanceStatus == 'EN_ROUTE_TO_ACCIDENT')
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Container(
                            padding: const EdgeInsets.all(16),
                            color: AppTheme.infoBlue.withOpacity(0.2),
                            child: Column(
                              children: [
                                const Text('EN ROUTE TO ACCIDENT', style: TextStyle(color: AppTheme.infoBlueLight, fontWeight: FontWeight.bold)),
                                const SizedBox(height: 8),
                                if (incident.currentRoute != null) ...[
                                  Text('ETA: ${incident.currentRoute!.etaMinutes} minutes', style: const TextStyle(fontSize: 24)),
                                  if (incident.currentRoute!.isBlocked)
                                    const Text('REROUTED DUE TO BLOCKAGE', style: TextStyle(color: AppTheme.emergencyOrange, fontWeight: FontWeight.bold)),
                                ]
                              ],
                            ),
                          ),
                          const SizedBox(height: 24),
                          ElevatedButton(
                            onPressed: () => provider.ambulanceArrivedAtAccident(),
                            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.successGreen, padding: const EdgeInsets.symmetric(vertical: 20)),
                            child: const Text('ARRIVED AT ACCIDENT SCENE', style: TextStyle(fontSize: 18)),
                          ),
                        ],
                      )
                    else if (incident.ambulanceStatus == 'ARRIVED')
                      ElevatedButton(
                        onPressed: () => provider.patientPickedUp(),
                        style: ElevatedButton.styleFrom(backgroundColor: AppTheme.successGreen, padding: const EdgeInsets.symmetric(vertical: 20)),
                        child: const Text('PATIENT PICKED UP & STABILIZED', style: TextStyle(fontSize: 18)),
                      )
                    else if (incident.ambulanceStatus == 'EN_ROUTE_TO_HOSPITAL')
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Container(
                            padding: const EdgeInsets.all(16),
                            color: AppTheme.emergencyOrange.withOpacity(0.2),
                            child: Column(
                              children: [
                                const Text('EN ROUTE TO HOSPITAL', style: TextStyle(color: AppTheme.emergencyOrange, fontWeight: FontWeight.bold)),
                                const SizedBox(height: 8),
                                Text('Destination: ${incident.assignedHospital?.name ?? "Unknown"}', style: const TextStyle(fontSize: 18)),
                              ],
                            ),
                          ),
                          const SizedBox(height: 24),
                          ElevatedButton(
                            onPressed: () => provider.patientArrived(),
                            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.successGreen, padding: const EdgeInsets.symmetric(vertical: 20)),
                            child: const Text('ARRIVED AT HOSPITAL', style: TextStyle(fontSize: 18)),
                          ),
                        ],
                      )
                    else if (incident.ambulanceStatus == 'AT_HOSPITAL')
                      const Center(child: Text('Handover in progress at hospital...', style: TextStyle(fontSize: 18, color: AppTheme.textMuted))),
                  ],
                ),
              ),
            ),
            Expanded(
              flex: 1,
              child: Container(
                color: AppTheme.darkCardLight,
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('NAVIGATION MAP', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 16),
                    Expanded(
                      child: Container(
                        decoration: BoxDecoration(
                          color: AppTheme.darkCard,
                          border: Border.all(color: AppTheme.divider),
                        ),
                        child: Center(
                          child: incident.currentRoute != null 
                            ? Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  const Icon(Icons.navigation, size: 48, color: AppTheme.infoBlueLight),
                                  const SizedBox(height: 16),
                                  Text(incident.currentRoute!.name, textAlign: TextAlign.center),
                                  if (incident.currentRoute!.isBlocked)
                                    const Text('\nAVOIDING BLOCKED ROAD', style: TextStyle(color: AppTheme.emergencyOrange)),
                                ],
                              )
                            : const Text('Awaiting Route Data'),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildInfoRow(String label, String value, Color valueColor) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        children: [
          SizedBox(width: 100, child: Text(label, style: const TextStyle(color: AppTheme.textSecondary))),
          Text(value, style: TextStyle(fontWeight: FontWeight.bold, color: valueColor, fontSize: 16)),
        ],
      ),
    );
  }
}
