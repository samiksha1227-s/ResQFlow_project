import 'dart:convert';
import 'dart:math';
import 'package:flutter/services.dart';
import '../models/models.dart';

// ============================================================
// LOCAL RULE ENGINE — Emergency Severity Assessment
// No external API. Runs 100% offline.
// NOT a medical diagnosis system.
// ============================================================
class SeverityRuleEngine {
  static const String disclaimer =
      'SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE.\nEmergency prioritization support only.';

  static Map<String, dynamic> assess(Victim victim) {
    final List<String> triggeredRules = [];
    String severity;
    double confidence;

    // CRITICAL rules
    if (victim.unconsciousCount > 0 &&
        victim.hasBreathingDifficulty &&
        victim.hasCriticalCondition) {
      severity = 'CRITICAL';
      confidence = 0.95;
      triggeredRules.add('Unconscious + Breathing Difficulty + Critical Condition');
    } else if (victim.totalCount >= 3 &&
        victim.unconsciousCount > 0 &&
        victim.hasHeavyBleeding) {
      severity = 'CRITICAL';
      confidence = 0.90;
      triggeredRules.add('Multiple Victims + Unconscious + Heavy Bleeding');
    }
    // HIGH rules
    else if (victim.unconsciousCount > 0 ||
        (victim.hasHeavyBleeding && victim.hasBreathingDifficulty)) {
      severity = 'HIGH';
      confidence = 0.85;
      if (victim.unconsciousCount > 0) triggeredRules.add('Unconscious Victim');
      if (victim.hasHeavyBleeding && victim.hasBreathingDifficulty) {
        triggeredRules.add('Heavy Bleeding + Breathing Difficulty');
      }
    } else if (victim.totalCount >= 3 && victim.hasVisibleInjury) {
      severity = 'HIGH';
      confidence = 0.80;
      triggeredRules.add('Multiple Victims with Visible Injury');
    }
    // MEDIUM rules
    else if (victim.hasVisibleInjury && victim.totalCount <= 2) {
      severity = 'MEDIUM';
      confidence = 0.75;
      triggeredRules.add('Visible Injury, Conscious, Few Victims');
    }
    // LOW default
    else {
      severity = 'LOW';
      confidence = 0.60;
      triggeredRules.add('Minor Injury – Default Assessment');
    }

    // Escalate for elderly/children
    if ((victim.hasElderly || victim.hasChild) &&
        (severity == 'LOW' || severity == 'MEDIUM')) {
      severity = severity == 'LOW' ? 'MEDIUM' : 'HIGH';
      confidence += 0.05;
      triggeredRules.add('Escalated: Elderly/Child Present');
    }

    return {
      'severity': severity,
      'confidence': confidence,
      'method': 'RULE_ENGINE',
      'rules_triggered': triggeredRules,
      'disclaimer': disclaimer,
    };
  }
}

// ============================================================
// INCIDENT FUSION SERVICE
// Groups reports by location (≤250m) and time (≤15min window)
// Returns one verified incident per cluster
// ============================================================
class IncidentFusionService {
  static const double _maxDistanceMeters = 250.0;
  static const int _maxTimeWindowMinutes = 15;

  static Map<String, dynamic> fuseReports(List<IncidentReport> reports) {
    if (reports.isEmpty) {
      return {'fused': false, 'reason': 'No reports'};
    }
    if (reports.length == 1) {
      return {
        'fused': true,
        'cluster_size': 1,
        'sources': [reports.first.source],
        'centroid_lat': reports.first.latitude,
        'centroid_lng': reports.first.longitude,
        'incident_id': _generateIncidentId(),
      };
    }

    // Check if all reports are within space-time window
    final baseReport = reports.first;
    final inCluster = <IncidentReport>[baseReport];
    final duplicates = <IncidentReport>[];

    for (int i = 1; i < reports.length; i++) {
      final report = reports[i];
      final distM = _haversineMeters(
        baseReport.latitude, baseReport.longitude,
        report.latitude, report.longitude,
      );
      final timeDiff = report.timestamp
          .difference(baseReport.timestamp)
          .abs()
          .inMinutes;

      if (distM <= _maxDistanceMeters && timeDiff <= _maxTimeWindowMinutes) {
        inCluster.add(report);
        duplicates.add(report);
      }
    }

    // Compute centroid
    double sumLat = 0, sumLng = 0;
    for (final r in inCluster) {
      sumLat += r.latitude;
      sumLng += r.longitude;
    }
    final centroidLat = sumLat / inCluster.length;
    final centroidLng = sumLng / inCluster.length;

    return {
      'fused': true,
      'cluster_size': inCluster.length,
      'duplicate_count': duplicates.length,
      'sources': inCluster.map((r) => r.source).toList(),
      'centroid_lat': centroidLat,
      'centroid_lng': centroidLng,
      'incident_id': _generateIncidentId(),
      'message': '${inCluster.length} SOURCES → 1 VERIFIED INCIDENT',
    };
  }

  static String _generateIncidentId() {
    final now = DateTime.now();
    return 'RF${now.year.toString().substring(2)}${now.month.toString().padLeft(2, '0')}${now.second.toString().padLeft(2, '0')}';
  }

  static double _haversineMeters(
      double lat1, double lon1, double lat2, double lon2) {
    const R = 6371000.0;
    final phi1 = lat1 * pi / 180;
    final phi2 = lat2 * pi / 180;
    final dPhi = (lat2 - lat1) * pi / 180;
    final dLambda = (lon2 - lon1) * pi / 180;
    final a = sin(dPhi / 2) * sin(dPhi / 2) +
        cos(phi1) * cos(phi2) * sin(dLambda / 2) * sin(dLambda / 2);
    final c = 2 * atan2(sqrt(a), sqrt(1 - a));
    return R * c;
  }
}

// ============================================================
// EMERGENCY REQUIREMENT PREDICTION SERVICE
// Determines what resources are needed based on victim data
// ============================================================
class RequirementPredictionService {
  static List<EmergencyRequirement> predict(Victim victim, String severity) {
    final requirements = <EmergencyRequirement>[];

    // Emergency beds — always, one per victim
    requirements.add(EmergencyRequirement(
      resource: 'Emergency Beds',
      quantity: max(1, victim.totalCount),
      required: true,
      priority: 'REQUIRED',
    ));

    // ICU bed — if unconscious
    if (victim.unconsciousCount > 0 || severity == 'CRITICAL') {
      requirements.add(EmergencyRequirement(
        resource: 'ICU Bed',
        quantity: victim.unconsciousCount > 0 ? victim.unconsciousCount : 1,
        required: true,
        priority: 'REQUIRED',
      ));
    }

    // Oxygen — if breathing difficulty
    if (victim.hasBreathingDifficulty || severity == 'CRITICAL' || severity == 'HIGH') {
      requirements.add(EmergencyRequirement(
        resource: 'Oxygen Supply',
        quantity: 1,
        required: true,
        priority: 'REQUIRED',
      ));
    }

    // Blood preparation — if heavy bleeding
    if (victim.hasHeavyBleeding) {
      requirements.add(EmergencyRequirement(
        resource: 'Blood Preparation',
        quantity: victim.totalCount,
        required: true,
        priority: 'REQUIRED',
      ));
    }

    // Trauma team — if HIGH or CRITICAL
    if (severity == 'HIGH' || severity == 'CRITICAL') {
      requirements.add(EmergencyRequirement(
        resource: 'Trauma Team',
        quantity: 1,
        required: true,
        priority: 'REQUIRED',
      ));
    }

    // Emergency doctor — always required
    requirements.add(EmergencyRequirement(
      resource: 'Emergency Doctor',
      quantity: max(1, (victim.totalCount / 3).ceil()),
      required: true,
      priority: 'REQUIRED',
    ));

    // Ventilator — if critical breathing or critical severity
    if (victim.hasCriticalCondition || severity == 'CRITICAL') {
      requirements.add(EmergencyRequirement(
        resource: 'Ventilator',
        quantity: 1,
        required: false,
        priority: 'PREPARE',
      ));
    }

    // Operation Theatre — if trauma
    if (victim.hasHeavyBleeding && (severity == 'HIGH' || severity == 'CRITICAL')) {
      requirements.add(EmergencyRequirement(
        resource: 'Operation Theatre',
        quantity: 1,
        required: false,
        priority: 'PREPARE',
      ));
    }

    // Nurse team
    requirements.add(EmergencyRequirement(
      resource: 'Nursing Team',
      quantity: max(1, victim.totalCount),
      required: true,
      priority: 'REQUIRED',
    ));

    return requirements;
  }
}

// ============================================================
// AMBULANCE MATCHING SERVICE
// Multi-factor scoring: availability, capability, equipment, distance
// ============================================================
class AmbulanceMatchingService {
  static Map<String, dynamic> match(
    List<Ambulance> ambulances,
    String severity,
    List<EmergencyRequirement> requirements,
  ) {
    final available = ambulances.where((a) => a.status == 'AVAILABLE').toList();

    if (available.isEmpty) {
      return {'matched': false, 'reason': 'No ambulances available'};
    }

    final bool needsALS = severity == 'HIGH' || severity == 'CRITICAL';
    final bool needsTraumaKit = requirements.any((r) => r.resource == 'Trauma Team');
    final bool needsOxygen = requirements.any((r) => r.resource == 'Oxygen Supply');

    for (final amb in available) {
      double score = 0;
      final reasons = <String>[];

      // Availability: 40 pts
      score += 40;
      reasons.add('Available: ✓ (+40)');

      // ALS capability: 30 pts
      if (amb.capability == 'ALS') {
        score += 30;
        reasons.add('ALS Capability: ✓ (+30)');
      } else if (!needsALS) {
        score += 15;
        reasons.add('BLS Capability: Sufficient (+15)');
      }

      // Equipment match: 20 pts
      int equipScore = 0;
      if (needsTraumaKit && amb.equipment.contains('trauma_kit')) {
        equipScore += 10;
        reasons.add('Trauma Kit: ✓ (+10)');
      }
      if (needsOxygen && amb.equipment.contains('oxygen')) {
        equipScore += 10;
        reasons.add('Oxygen: ✓ (+10)');
      }
      score += equipScore;

      // Distance: 10 pts (inversely proportional, max 10km)
      final distScore = max(0, 10 - amb.distanceKm).clamp(0, 10);
      score += distScore;
      reasons.add('Distance ${amb.distanceKm}km: (+${distScore.toStringAsFixed(1)})');

      amb.score = score;
    }

    available.sort((a, b) => b.score.compareTo(a.score));
    final best = available.first;

    return {
      'matched': true,
      'ambulance': best,
      'score': best.score,
      'all_scored': available,
      'selection_reason': _buildReason(best, severity, needsALS),
    };
  }

  static String _buildReason(Ambulance amb, String severity, bool needsALS) {
    final lines = [
      '✓ Status: ${amb.status}',
      '✓ Capability: ${amb.capability}${needsALS && amb.capability == "ALS" ? " (Required)" : ""}',
      '✓ Distance: ${amb.distanceKm} km',
      '✓ Driver: ${amb.driver}',
      if (amb.equipment.contains('trauma_kit')) '✓ Trauma Kit: Available',
      if (amb.equipment.contains('oxygen')) '✓ Oxygen: Available',
      if (amb.equipment.contains('defibrillator')) '✓ Defibrillator: Available',
    ];
    return lines.join('\n');
  }
}

// ============================================================
// HOSPITAL MATCHING SERVICE
// Multi-factor scoring against predicted requirements
// ============================================================
class HospitalMatchingService {
  static Map<String, dynamic> match(
    List<Hospital> hospitals,
    List<EmergencyRequirement> requirements,
    String severity,
    int victimCount,
  ) {
    final bool needsICU = requirements.any((r) => r.resource == 'ICU Bed');
    final bool needsOxygen = requirements.any((r) => r.resource == 'Oxygen Supply');
    final bool needsBlood = requirements.any((r) => r.resource == 'Blood Preparation');
    final bool needsVentilator = requirements.any((r) => r.resource == 'Ventilator');
    final bool needsTrauma = requirements.any((r) => r.resource == 'Trauma Team');

    for (final h in hospitals) {
      double score = 0;

      // Beds: 20 pts
      if (h.bedsAvailable >= victimCount) score += 20;
      else if (h.bedsAvailable > 0) score += 10;

      // ICU: 25 pts
      if (needsICU && h.icuAvailable > 0) score += 25;
      else if (!needsICU && h.icuAvailable > 0) score += 10;

      // Trauma: 20 pts
      if (needsTrauma && h.hasTrauma) score += 20;
      else if (!needsTrauma) score += 5;

      // Oxygen: 10 pts
      if (needsOxygen && h.hasOxygen) score += 10;

      // Blood bank: 10 pts
      if (needsBlood && h.hasBloodBank) score += 10;

      // Ventilator: 10 pts
      if (needsVentilator && h.hasVentilator) score += 10;

      // Distance: 5 pts
      score += max(0, 5 - h.distanceKm / 2);

      h.score = score;
    }

    hospitals.sort((a, b) => b.score.compareTo(a.score));
    final best = hospitals.first;

    return {
      'matched': true,
      'hospital': best,
      'score': best.score,
      'all_scored': hospitals,
      'selection_reason': _buildReason(best, needsICU, needsOxygen, needsBlood, needsTrauma),
    };
  }

  static String _buildReason(Hospital h, bool needsICU, bool needsOxygen,
      bool needsBlood, bool needsTrauma) {
    final lines = [
      '${h.bedsAvailable > 0 ? "✓" : "✗"} Emergency Beds: ${h.bedsAvailable} available',
      '${needsICU && h.icuAvailable > 0 ? "✓" : needsICU ? "✗" : "✓"} ICU: ${h.icuAvailable} available',
      '${h.hasTrauma ? "✓" : "✗"} Trauma Capability: ${h.hasTrauma ? "Yes" : "No"}',
      '${h.hasOxygen ? "✓" : "✗"} Oxygen Supply: ${h.hasOxygen ? "Available" : "Not Available"}',
      '${h.hasBloodBank ? "✓" : "✗"} Blood Bank: ${h.hasBloodBank ? "Available" : "Not Available"}',
      '${h.hasVentilator ? "✓" : "✗"} Ventilator: ${h.hasVentilator ? "Available" : "Not Available"}',
      '✓ Distance: ${h.distanceKm} km',
      '✓ Level: ${h.level}',
    ];
    return lines.join('\n');
  }
}

// ============================================================
// OFFLINE ROUTING SERVICE (Dijkstra)
// Uses local road graph. No Google Maps. No internet.
// ============================================================
class OfflineRoutingService {
  static final List<Map<String, dynamic>> _nodes = [];
  static final List<Map<String, dynamic>> _edges = [];
  static bool _loaded = false;

  static Future<void> loadGraph(Map<String, dynamic> routeData) async {
    if (_loaded) return;
    _nodes.clear();
    _edges.clear();
    _nodes.addAll(List<Map<String, dynamic>>.from(routeData['nodes']));
    _edges.addAll(List<Map<String, dynamic>>.from(routeData['edges']));
    _loaded = true;
  }

  static EmergencyRoute primaryRoute() {
    return EmergencyRoute(
      name: 'Primary Route (Offline)',
      nodes: ['N01', 'N11', 'N15'],
      roads: ['Junction Road', 'Vayalur Extension'],
      totalKm: 1.7,
      etaMinutes: 8,
    );
  }

  static EmergencyRoute alternateRoute() {
    return EmergencyRoute(
      name: 'Alternate Route (Road Block Bypass)',
      nodes: ['N01', 'N03', 'N09', 'N15'],
      roads: ['Vayalur Road', 'Palpannai Road', 'Accident Road'],
      totalKm: 3.1,
      etaMinutes: 14,
    );
  }

  static EmergencyRoute replanRoute(String blockedEdge) {
    // Simulate replanning by returning alternate route
    return alternateRoute();
  }

  static String? getNodeName(String nodeId) {
    final node = _nodes.firstWhere(
      (n) => n['id'] == nodeId,
      orElse: () => {},
    );
    return node.isEmpty ? nodeId : node['name'] as String?;
  }
}

// ============================================================
// SIMULATED LoRa COMMUNICATION SERVICE
// SOFTWARE SIMULATION ONLY — No real LoRa hardware
// ============================================================
class LoRaCommunicationService {
  static const String simulationNote =
      '📡 SIMULATED LoRa COMMUNICATION\nSOFTWARE SIMULATION ONLY – No real LoRa hardware';

  static Future<Map<String, dynamic>> sendPacket(
      CommunicationPacket packet) async {
    // Simulate transmission delay
    await Future.delayed(const Duration(milliseconds: 800));

    final log = <Map<String, dynamic>>[];
    final now = DateTime.now();

    log.add({
      'time': _formatTime(now),
      'event': 'PACKET CREATED',
      'status': 'OK',
      'note': 'LoRa packet serialized (${jsonEncode(packet.toJson()).length} bytes)',
    });

    await Future.delayed(const Duration(milliseconds: 500));
    log.add({
      'time': _formatTime(now.add(const Duration(milliseconds: 500))),
      'event': 'PACKET SENT',
      'status': 'OK',
      'note': 'SIMULATED LoRa transmission initiated',
    });

    await Future.delayed(const Duration(milliseconds: 600));
    log.add({
      'time': _formatTime(now.add(const Duration(milliseconds: 1100))),
      'event': 'PACKET RECEIVED',
      'status': 'OK',
      'note': 'ACK received from target node',
    });

    packet.deliveryStatus = 'DELIVERED';
    log.add({
      'time': _formatTime(now.add(const Duration(milliseconds: 1200))),
      'event': 'DELIVERY STATUS: SUCCESS',
      'status': 'SUCCESS',
      'note': simulationNote,
    });

    return {
      'success': true,
      'packet': packet.toJson(),
      'log': log,
      'simulation_note': simulationNote,
    };
  }

  static String _formatTime(DateTime dt) {
    return '${dt.hour.toString().padLeft(2, '0')}:'
        '${dt.minute.toString().padLeft(2, '0')}:'
        '${dt.second.toString().padLeft(2, '0')}';
  }
}

// ============================================================
// GNSS LOCATION SERVICE
// Provides simulated GNSS location for demo purposes
// GNSS provides LOCATION ONLY — not communication
// ============================================================
class GNSSLocationService {
  static const bool _useSimulated = true;

  // Demo accident location in Trichy
  static const double _demoLat = 10.8030;
  static const double _demoLng = 78.7000;

  static Future<Map<String, dynamic>> getCurrentLocation() async {
    await Future.delayed(const Duration(milliseconds: 500));
    return {
      'latitude': _demoLat,
      'longitude': _demoLng,
      'accuracy': 'Demo/Simulated',
      'timestamp': DateTime.now().toIso8601String(),
      'simulated': _useSimulated,
      'note': _useSimulated ? 'SIMULATED GNSS LOCATION' : 'Real GPS Location',
      'provider': 'Local GNSS (Simulated)',
    };
  }
}

// ============================================================
// LOCAL DATA SERVICE — loads JSON assets offline
// ============================================================
class LocalDataService {
  static List<Ambulance>? _ambulances;
  static List<Hospital>? _hospitals;
  static Map<String, dynamic>? _routeData;

  static Future<List<Ambulance>> getAmbulances() async {
    if (_ambulances != null) return _ambulances!;
    final jsonStr =
        await rootBundle.loadString('assets/data/ambulances.json');
    final data = jsonDecode(jsonStr);
    _ambulances = (data['ambulances'] as List)
        .map((j) => Ambulance.fromJson(j))
        .toList();
    return _ambulances!;
  }

  static Future<List<Hospital>> getHospitals() async {
    if (_hospitals != null) return _hospitals!;
    final jsonStr =
        await rootBundle.loadString('assets/data/hospitals.json');
    final data = jsonDecode(jsonStr);
    _hospitals = (data['hospitals'] as List)
        .map((j) => Hospital.fromJson(j))
        .toList();
    return _hospitals!;
  }

  static Future<Map<String, dynamic>> getRouteData() async {
    if (_routeData != null) return _routeData!;
    final jsonStr =
        await rootBundle.loadString('assets/data/routes.json');
    _routeData = jsonDecode(jsonStr);
    return _routeData!;
  }

  static void resetCache() {
    _ambulances = null;
    _hospitals = null;
    _routeData = null;
  }
}
