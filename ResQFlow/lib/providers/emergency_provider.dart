import 'package:flutter/foundation.dart';
import '../models/models.dart';
import '../services/local_services.dart';

enum AppRole { citizen, ambulance, hospital, controlRoom }

class EmergencyProvider extends ChangeNotifier {
  // ── App State ──────────────────────────────────────────────
  AppRole selectedRole = AppRole.controlRoom;
  bool isOffline = true; // Always offline-first
  String offlineStatus = '🔴 OFFLINE MODE – CORE EMERGENCY SERVICES ACTIVE';

  // ── Current Incident ───────────────────────────────────────
  VerifiedIncident? currentIncident;
  String incidentIdCounter = 'RF001';

  // ── Demo Source Reports ────────────────────────────────────
  final List<IncidentReport> sourceReports = [];
  Map<String, dynamic>? fusionResult;

  // ── Resources ──────────────────────────────────────────────
  List<Ambulance> ambulances = [];
  List<Hospital> hospitals = [];
  Map<String, dynamic>? routeData;

  // ── Communication ──────────────────────────────────────────
  final List<Map<String, dynamic>> communicationLog = [];
  CommunicationPacket? lastPacket;

  // ── Incidents History ──────────────────────────────────────
  final List<VerifiedIncident> incidentHistory = [];

  // ── Control Room Stats ─────────────────────────────────────
  int get activeIncidents => currentIncident != null &&
      currentIncident!.status != 'CLOSED' ? 1 : 0;
  int get criticalIncidents => currentIncident != null &&
      currentIncident!.severity == 'CRITICAL' ? 1 : 0;
  int get ambulancesAvailable =>
      ambulances.where((a) => a.status == 'AVAILABLE').length;
  int get ambulancesEnRoute =>
      ambulances.where((a) => a.status == 'EN_ROUTE').length;
  int get hospitalsReady =>
      hospitals.where((h) => h.status == 'READY').length;

  // ── Initialization ─────────────────────────────────────────
  Future<void> initialize() async {
    await _loadLocalData();
    _addLog('ResQFlow AI Initialized', 'SYSTEM', 'OFFLINE MODE ACTIVE');
    notifyListeners();
  }

  Future<void> _loadLocalData() async {
    ambulances = await LocalDataService.getAmbulances();
    hospitals = await LocalDataService.getHospitals();
    routeData = await LocalDataService.getRouteData();
    if (routeData != null) {
      await OfflineRoutingService.loadGraph(routeData!);
    }
  }

  // ── Role Selection ─────────────────────────────────────────
  void selectRole(AppRole role) {
    selectedRole = role;
    notifyListeners();
  }

  // ── STEP 1: Simulate Accident & Add Source Reports ─────────
  void simulateAccident() {
    sourceReports.clear();
    fusionResult = null;
    currentIncident = null;

    final base = DateTime.now();

    sourceReports.addAll([
      IncidentReport(
        id: 'R001',
        source: 'CCTV',
        latitude: 10.8030,
        longitude: 78.7000,
        timestamp: base,
        description: 'Vehicle collision detected. Multiple vehicles involved.',
      ),
      IncidentReport(
        id: 'R002',
        source: 'CITIZEN',
        latitude: 10.8031,
        longitude: 78.6999,
        timestamp: base.add(const Duration(seconds: 2)),
        description: 'Accident reported. People injured on road.',
      ),
      IncidentReport(
        id: 'R003',
        source: 'DASHCAM',
        latitude: 10.8029,
        longitude: 78.7001,
        timestamp: base.add(const Duration(seconds: 3)),
        description: 'Crash detected by dashcam impact sensor.',
      ),
      IncidentReport(
        id: 'R004',
        source: 'AUTHORITY',
        latitude: 10.8030,
        longitude: 78.7000,
        timestamp: base.add(const Duration(seconds: 8)),
        description: 'Traffic authority reported accident at junction.',
      ),
    ]);

    _addLog('Accident simulation triggered', 'SYSTEM', 'DEMO');
    _addLog('4 incident reports generated', 'INCIDENT', 'SOURCES: CCTV, CITIZEN, DASHCAM, AUTHORITY');
    notifyListeners();
  }

  void addManualReport({
    required String source,
    required double lat,
    required double lng,
    required String description,
  }) {
    sourceReports.add(IncidentReport(
      id: 'R${sourceReports.length + 1}',
      source: source,
      latitude: lat,
      longitude: lng,
      timestamp: DateTime.now(),
      description: description,
    ));
    _addLog('Manual report added', source, description);
    notifyListeners();
  }

  // ── STEP 2: Run Incident Fusion ────────────────────────────
  Future<void> runIncidentFusion() async {
    if (sourceReports.isEmpty) return;

    fusionResult = IncidentFusionService.fuseReports(sourceReports);

    if (fusionResult!['fused'] == true) {
      incidentIdCounter = fusionResult!['incident_id'] ?? 'RF001';

      currentIncident = VerifiedIncident(
        incidentId: incidentIdCounter,
        status: 'FUSED',
        reports: List.from(sourceReports),
        latitude: fusionResult!['centroid_lat'],
        longitude: fusionResult!['centroid_lng'],
        detectedAt: DateTime.now(),
        requirements: [],
        timeline: [],
        communicationLog: [],
      );
      currentIncident!.timeline = [
        TimelineEvent(
          event: 'INCIDENT DETECTED',
          timestamp: sourceReports.first.timestamp,
          details: '${sourceReports.length} source reports received',
          status: 'INFO',
        ),
        TimelineEvent(
          event: 'AI INCIDENT FUSION RUN',
          timestamp: DateTime.now(),
          details: '${sourceReports.length} sources → 1 verified incident',
          status: 'SUCCESS',
        ),
      ];

      _addLog('Incident fusion complete', 'FUSION', fusionResult!['message'] ?? '');
      _addLog('Incident ID generated: $incidentIdCounter', 'SYSTEM', 'VERIFIED');
    }
    notifyListeners();
  }

  // ── STEP 3: Verify Incident ────────────────────────────────
  void verifyIncident() {
    if (currentIncident == null) return;
    currentIncident!.status = 'VERIFIED';
    currentIncident!.timeline.add(TimelineEvent(
      event: 'INCIDENT VERIFIED',
      timestamp: DateTime.now(),
      details: 'Incident $incidentIdCounter verified by system',
      status: 'SUCCESS',
    ));
    _addLog('Incident $incidentIdCounter VERIFIED', 'SYSTEM', '');
    notifyListeners();
  }

  // ── STEP 4: Add Victim Data ────────────────────────────────
  void addVictimData(Victim victim) {
    if (currentIncident == null) return;
    currentIncident!.victims = victim;
    currentIncident!.status = 'ASSESSED';
    currentIncident!.timeline.add(TimelineEvent(
      event: 'VICTIM INFORMATION RECORDED',
      timestamp: DateTime.now(),
      details: '${victim.totalCount} victims, ${victim.unconsciousCount} unconscious',
      status: 'INFO',
    ));
    _addLog('Victim data recorded', 'INCIDENT', '${victim.totalCount} victims');
    notifyListeners();
  }

  // ── STEP 5: Run Severity Assessment ───────────────────────
  void runSeverityAssessment() {
    if (currentIncident?.victims == null) return;
    final result = SeverityRuleEngine.assess(currentIncident!.victims!);
    currentIncident!.severity = result['severity'];
    currentIncident!.status = 'ASSESSED';
    currentIncident!.timeline.add(TimelineEvent(
      event: 'SEVERITY ASSESSED',
      timestamp: DateTime.now(),
      details:
          '${result['severity']} (${(result['confidence'] * 100).toStringAsFixed(0)}% confidence)\nMethod: ${result['method']}',
      status: result['severity'] == 'CRITICAL' || result['severity'] == 'HIGH'
          ? 'WARNING'
          : 'INFO',
    ));
    _addLog('Severity: ${result['severity']}', 'SEVERITY', result['method']);
    notifyListeners();
  }

  // ── STEP 6: Predict Requirements ──────────────────────────
  void predictRequirements() {
    if (currentIncident?.victims == null || currentIncident?.severity == null) return;
    currentIncident!.requirements = RequirementPredictionService.predict(
      currentIncident!.victims!,
      currentIncident!.severity!,
    );
    currentIncident!.status = 'REQUIREMENTS_PREDICTED';
    currentIncident!.timeline.add(TimelineEvent(
      event: 'EMERGENCY REQUIREMENTS PREDICTED',
      timestamp: DateTime.now(),
      details:
          '${currentIncident!.requirements.length} resource types identified',
      status: 'SUCCESS',
    ));
    _addLog('Requirements predicted', 'AI', '${currentIncident!.requirements.length} resources');
    notifyListeners();
  }

  // ── STEP 7: Match Ambulance ────────────────────────────────
  Future<void> matchAmbulance() async {
    if (currentIncident == null) return;

    final result = AmbulanceMatchingService.match(
      List.from(ambulances),
      currentIncident!.severity ?? 'HIGH',
      currentIncident!.requirements,
    );

    if (result['matched'] == true) {
      currentIncident!.assignedAmbulance = result['ambulance'];
      currentIncident!.status = 'AMBULANCE_MATCHED';
      currentIncident!.timeline.add(TimelineEvent(
        event: 'AMBULANCE MATCHED',
        timestamp: DateTime.now(),
        details:
            '${result['ambulance'].id} selected (Score: ${result['score'].toStringAsFixed(0)})',
        status: 'SUCCESS',
      ));
      _addLog('Ambulance ${result['ambulance'].id} selected', 'DISPATCH', '');
    }
    notifyListeners();
  }

  // ── STEP 8: Send Ambulance Alert (Simulated LoRa) ──────────
  Future<void> sendAmbulanceAlert() async {
    if (currentIncident?.assignedAmbulance == null) return;

    final packet = CommunicationPacket(
      incidentId: currentIncident!.incidentId,
      severity: currentIncident!.severity ?? 'HIGH',
      victims: currentIncident!.victims?.totalCount ?? 0,
      latitude: currentIncident!.latitude,
      longitude: currentIncident!.longitude,
      ambulanceId: currentIncident!.assignedAmbulance!.id,
      hospitalId: currentIncident!.assignedHospital?.id ?? 'TBD',
      messageType: 'AMBULANCE_DISPATCH',
      timestamp: DateTime.now(),
    );

    final result = await LoRaCommunicationService.sendPacket(packet);
    lastPacket = packet;

    final logEntries = result['log'] as List<Map<String, dynamic>>;
    communicationLog.addAll(logEntries);

    currentIncident!.timeline.add(TimelineEvent(
      event: 'AMBULANCE ALERT SENT (SIMULATED LoRa)',
      timestamp: DateTime.now(),
      details: 'Packet delivered to ${currentIncident!.assignedAmbulance!.id}',
      status: 'SUCCESS',
    ));
    _addLog('Ambulance alert sent (SIMULATED LoRa)', 'COMM', packet.ambulanceId);
    notifyListeners();
  }

  // ── STEP 9: Ambulance Actions ─────────────────────────────
  void acceptEmergency() {
    if (currentIncident?.assignedAmbulance == null) return;
    currentIncident!.ambulanceStatus = 'EN_ROUTE_TO_ACCIDENT';
    currentIncident!.status = 'ROUTE_ACTIVE';

    // Assign primary route
    currentIncident!.currentRoute = OfflineRoutingService.primaryRoute();
    currentIncident!.etaToAccident =
        DateTime.now().add(Duration(
          minutes: currentIncident!.currentRoute!.etaMinutes,
        ));

    // Mark ambulance as en route
    final ambIdx = ambulances.indexWhere(
        (a) => a.id == currentIncident!.assignedAmbulance!.id);
    if (ambIdx >= 0) ambulances[ambIdx].status = 'EN_ROUTE';

    currentIncident!.timeline.add(TimelineEvent(
      event: 'AMBULANCE ACCEPTED EMERGENCY',
      timestamp: DateTime.now(),
      details: '${currentIncident!.assignedAmbulance!.id} EN ROUTE TO ACCIDENT\nETA: ${currentIncident!.currentRoute!.etaMinutes} minutes',
      status: 'SUCCESS',
    ));
    _addLog('Emergency accepted by ${currentIncident!.assignedAmbulance!.id}', 'AMBULANCE', 'EN_ROUTE');
    notifyListeners();
  }

  // ── STEP 10: Simulate Road Block + Replan ─────────────────
  void simulateRoadBlock() {
    if (currentIncident?.currentRoute == null) return;

    final oldRoute = currentIncident!.currentRoute!;
    oldRoute.isBlocked = true;

    final newRoute = OfflineRoutingService.replanRoute('N11');
    currentIncident!.currentRoute = newRoute;
    currentIncident!.etaToAccident =
        DateTime.now().add(Duration(minutes: newRoute.etaMinutes));

    currentIncident!.timeline.add(TimelineEvent(
      event: '🚧 ROAD BLOCK DETECTED',
      timestamp: DateTime.now(),
      details:
          'Junction Road BLOCKED\nAdaptive replanning triggered...',
      status: 'WARNING',
    ));
    currentIncident!.timeline.add(TimelineEvent(
      event: '🔄 EMERGENCY PLAN UPDATED',
      timestamp: DateTime.now().add(const Duration(seconds: 2)),
      details:
          'New route: ${newRoute.roads.join(" → ")}\nNew ETA: ${newRoute.etaMinutes} minutes',
      status: 'SUCCESS',
    ));
    _addLog('ROAD BLOCK – Adaptive Replanning triggered', 'ROUTING', newRoute.name);
    notifyListeners();
  }

  void ambulanceArrivedAtAccident() {
    if (currentIncident == null) return;
    currentIncident!.ambulanceStatus = 'ARRIVED';
    currentIncident!.timeline.add(TimelineEvent(
      event: 'AMBULANCE ARRIVED AT ACCIDENT',
      timestamp: DateTime.now(),
      details: '${currentIncident!.assignedAmbulance?.id} on scene',
      status: 'SUCCESS',
    ));
    notifyListeners();
  }

  void patientPickedUp() {
    if (currentIncident == null) return;
    currentIncident!.ambulanceStatus = 'EN_ROUTE_TO_HOSPITAL';
    currentIncident!.timeline.add(TimelineEvent(
      event: 'PATIENT PICKED UP',
      timestamp: DateTime.now(),
      details: 'En route to ${currentIncident!.assignedHospital?.name ?? "hospital"}',
      status: 'INFO',
    ));
    notifyListeners();
  }

  // ── STEP 11: Match Hospital ────────────────────────────────
  Future<void> matchHospital() async {
    if (currentIncident == null) return;

    final result = HospitalMatchingService.match(
      List.from(hospitals),
      currentIncident!.requirements,
      currentIncident!.severity ?? 'HIGH',
      currentIncident!.victims?.totalCount ?? 1,
    );

    if (result['matched'] == true) {
      currentIncident!.assignedHospital = result['hospital'];
      currentIncident!.status = 'HOSPITAL_MATCHED';
      currentIncident!.timeline.add(TimelineEvent(
        event: 'HOSPITAL MATCHED',
        timestamp: DateTime.now(),
        details:
            '${result['hospital'].name} selected (Score: ${result['score'].toStringAsFixed(0)})',
        status: 'SUCCESS',
      ));
      _addLog('Hospital ${result['hospital'].id} selected', 'HOSPITAL', '');
    }
    notifyListeners();
  }

  // ── STEP 12: Send Hospital Alert ───────────────────────────
  Future<void> sendHospitalAlert() async {
    if (currentIncident?.assignedHospital == null) return;

    final packet = CommunicationPacket(
      incidentId: currentIncident!.incidentId,
      severity: currentIncident!.severity ?? 'HIGH',
      victims: currentIncident!.victims?.totalCount ?? 0,
      latitude: currentIncident!.latitude,
      longitude: currentIncident!.longitude,
      ambulanceId: currentIncident!.assignedAmbulance?.id ?? 'N/A',
      hospitalId: currentIncident!.assignedHospital!.id,
      messageType: 'HOSPITAL_ALERT',
      timestamp: DateTime.now(),
    );

    final result = await LoRaCommunicationService.sendPacket(packet);
    communicationLog.addAll(result['log'] as List<Map<String, dynamic>>);

    // Initialize hospital preparations
    final hospital = currentIncident!.assignedHospital!;
    hospital.status = 'PREPARING';

    currentIncident!.status = 'HOSPITAL_PREPARING';
    currentIncident!.etaToHospital = DateTime.now().add(
      Duration(minutes: (hospital.distanceKm / 0.5).round() + 5),
    );

    currentIncident!.timeline.add(TimelineEvent(
      event: 'HOSPITAL ALERT SENT (SIMULATED LoRa)',
      timestamp: DateTime.now(),
      details:
          'Pre-arrival alert sent to ${hospital.name}\nHospital preparing resources...',
      status: 'SUCCESS',
    ));
    _addLog('Hospital alert sent to ${hospital.id}', 'COMM', hospital.name);
    notifyListeners();
  }

  // ── STEP 13: Hospital Readiness ────────────────────────────
  void markRequirementReady(int index) {
    if (currentIncident == null ||
        index >= currentIncident!.requirements.length) return;
    currentIncident!.requirements[index].isReady = true;

    final allCriticalReady = currentIncident!.requirements
        .where((r) => r.priority == 'REQUIRED')
        .every((r) => r.isReady);

    if (allCriticalReady && currentIncident!.assignedHospital != null) {
      currentIncident!.assignedHospital!.status = 'READY';
      currentIncident!.hospitalReady = true;
      currentIncident!.timeline.add(TimelineEvent(
        event: '🟢 HOSPITAL READY',
        timestamp: DateTime.now(),
        details:
            '${currentIncident!.assignedHospital!.name} – All critical resources prepared',
        status: 'SUCCESS',
      ));
      _addLog('HOSPITAL READY', 'HOSPITAL', currentIncident!.assignedHospital!.name);
    }
    notifyListeners();
  }

  void markAllRequirementsReady() {
    if (currentIncident == null) return;
    for (int i = 0; i < currentIncident!.requirements.length; i++) {
      currentIncident!.requirements[i].isReady = true;
    }
    if (currentIncident!.assignedHospital != null) {
      currentIncident!.assignedHospital!.status = 'READY';
      currentIncident!.hospitalReady = true;
      currentIncident!.timeline.add(TimelineEvent(
        event: '🟢 HOSPITAL READY – ALL RESOURCES PREPARED',
        timestamp: DateTime.now(),
        details: 'Ready for patient arrival',
        status: 'SUCCESS',
      ));
    }
    notifyListeners();
  }

  // ── STEP 14: Patient Arrival & Handover ───────────────────
  void patientArrived() {
    if (currentIncident == null) return;
    currentIncident!.ambulanceStatus = 'AT_HOSPITAL';
    currentIncident!.status = 'PATIENT_ARRIVED';
    currentIncident!.timeline.add(TimelineEvent(
      event: 'PATIENT ARRIVED AT HOSPITAL',
      timestamp: DateTime.now(),
      details:
          '${currentIncident!.victims?.totalCount ?? "?"} patients at ${currentIncident!.assignedHospital?.name}',
      status: 'SUCCESS',
    ));
    notifyListeners();
  }

  void completeHandover() {
    if (currentIncident == null) return;
    currentIncident!.status = 'HANDOVER';
    currentIncident!.timeline.add(TimelineEvent(
      event: 'PATIENT HANDOVER COMPLETE',
      timestamp: DateTime.now(),
      details: 'Patients handed over to hospital staff',
      status: 'SUCCESS',
    ));
    notifyListeners();
  }

  // ── STEP 15: Close Incident ────────────────────────────────
  void closeIncident() {
    if (currentIncident == null) return;
    currentIncident!.status = 'CLOSED';
    currentIncident!.timeline.add(TimelineEvent(
      event: '✅ INCIDENT CLOSED',
      timestamp: DateTime.now(),
      details: 'Emergency response completed. Incident $incidentIdCounter closed.',
      status: 'SUCCESS',
    ));

    // Restore ambulance
    if (currentIncident!.assignedAmbulance != null) {
      final ambIdx = ambulances.indexWhere(
          (a) => a.id == currentIncident!.assignedAmbulance!.id);
      if (ambIdx >= 0) ambulances[ambIdx].status = 'AVAILABLE';
    }

    incidentHistory.add(currentIncident!);
    _addLog('Incident $incidentIdCounter CLOSED', 'SYSTEM', '');
    notifyListeners();
  }

  // ── Demo Reset ─────────────────────────────────────────────
  Future<void> resetDemo() async {
    sourceReports.clear();
    fusionResult = null;
    currentIncident = null;
    communicationLog.clear();
    lastPacket = null;
    LocalDataService.resetCache();
    await _loadLocalData();
    _addLog('Demo reset complete', 'SYSTEM', 'Ready for new demo');
    notifyListeners();
  }

  // ── Logging ────────────────────────────────────────────────
  void _addLog(String event, String source, String details) {
    final now = DateTime.now();
    communicationLog.add({
      'time': '[${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}:${now.second.toString().padLeft(2, '0')}]',
      'event': event,
      'source': source,
      'details': details,
      'status': 'INFO',
    });
  }

  // ── Workflow progress ─────────────────────────────────────
  int get workflowStep {
    if (currentIncident == null) return 0;
    switch (currentIncident!.status) {
      case 'DETECTED': return 1;
      case 'FUSED': return 2;
      case 'VERIFIED': return 3;
      case 'ASSESSED': return 4;
      case 'REQUIREMENTS_PREDICTED': return 5;
      case 'AMBULANCE_MATCHED': return 6;
      case 'HOSPITAL_MATCHED': return 7;
      case 'HOSPITAL_PREPARING': return 8;
      case 'ROUTE_ACTIVE': return 9;
      case 'PATIENT_ARRIVED': return 10;
      case 'HANDOVER': return 11;
      case 'CLOSED': return 12;
      default: return 0;
    }
  }
}
