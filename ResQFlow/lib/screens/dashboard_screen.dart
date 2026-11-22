import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/emergency_provider.dart';
import '../theme/app_theme.dart';
import 'control/control_room_dashboard.dart';
import 'citizen/citizen_dashboard.dart';
import 'ambulance/ambulance_dashboard.dart';
import 'hospital/hospital_dashboard.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<EmergencyProvider>(
      builder: (context, provider, child) {
        return Scaffold(
          appBar: AppBar(
            title: const Text('ResQFlow AI'),
            actions: [
              DropdownButton<AppRole>(
                value: provider.selectedRole,
                dropdownColor: AppTheme.darkCard,
                underline: const SizedBox(),
                icon: const Icon(Icons.person, color: AppTheme.textPrimary),
                onChanged: (AppRole? newRole) {
                  if (newRole != null) provider.selectRole(newRole);
                },
                items: const [
                  DropdownMenuItem(
                    value: AppRole.controlRoom,
                    child: Text('Control Room', style: TextStyle(color: AppTheme.textPrimary)),
                  ),
                  DropdownMenuItem(
                    value: AppRole.citizen,
                    child: Text('Citizen', style: TextStyle(color: AppTheme.textPrimary)),
                  ),
                  DropdownMenuItem(
                    value: AppRole.ambulance,
                    child: Text('Ambulance A01', style: TextStyle(color: AppTheme.textPrimary)),
                  ),
                  DropdownMenuItem(
                    value: AppRole.hospital,
                    child: Text('Hospital H01', style: TextStyle(color: AppTheme.textPrimary)),
                  ),
                ],
              ),
              const SizedBox(width: 16),
            ],
          ),
          body: Column(
            children: [
              if (provider.isOffline)
                Container(
                  width: double.infinity,
                  color: AppTheme.offlineBanner,
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  child: Text(
                    provider.offlineStatus,
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.2,
                    ),
                  ),
                ),
              Expanded(
                child: _buildRoleView(provider.selectedRole),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildRoleView(AppRole role) {
    switch (role) {
      case AppRole.controlRoom:
        return const ControlRoomDashboard();
      case AppRole.citizen:
        return const CitizenDashboard();
      case AppRole.ambulance:
        return const AmbulanceDashboard();
      case AppRole.hospital:
        return const HospitalDashboard();
    }
  }
}
