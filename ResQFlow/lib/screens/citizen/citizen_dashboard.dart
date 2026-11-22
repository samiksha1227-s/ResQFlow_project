import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/emergency_provider.dart';
import '../../theme/app_theme.dart';

class CitizenDashboard extends StatelessWidget {
  const CitizenDashboard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<EmergencyProvider>(
      builder: (context, provider, _) {
        return Center(
          child: Container(
            constraints: const BoxConstraints(maxWidth: 500),
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Icon(Icons.warning_rounded, size: 80, color: AppTheme.emergencyRed),
                const SizedBox(height: 24),
                const Text(
                  'CITIZEN EMERGENCY SOS',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Report an emergency to the ResQFlow AI system.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: AppTheme.textSecondary),
                ),
                const SizedBox(height: 48),
                ElevatedButton(
                  onPressed: () {
                    provider.addManualReport(
                      source: 'CITIZEN',
                      lat: 10.8030,
                      lng: 78.7000,
                      description: 'Severe accident witnessed. Needs immediate help.',
                    );
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Report sent successfully (Simulated)'),
                        backgroundColor: AppTheme.successGreen,
                      ),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.emergencyRed,
                    padding: const EdgeInsets.symmetric(vertical: 24),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: const Text('REPORT ACCIDENT NOW', style: TextStyle(fontSize: 20)),
                ),
                const SizedBox(height: 24),
                OutlinedButton(
                  onPressed: () {},
                  child: const Text('CALL AMBULANCE (108)'),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
