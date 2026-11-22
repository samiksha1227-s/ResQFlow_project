// Core data models for ResQFlow AI

class IncidentReport {
  final String id;
  final String source; // CCTV, DASHCAM, CITIZEN, AUTHORITY
  final double latitude;
  final double longitude;
  final DateTime timestamp;
  final String description;
  final String? imageUrl;

  IncidentReport({
    required this.id,
    required this.source,
    required this.latitude,
    required this.longitude,
    required this.timestamp,
    required this.description,
    this.imageUrl,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'source': source,
        'latitude': latitude,
        'longitude': longitude,
        'timestamp': timestamp.toIso8601String(),
        'description': description,
      };
}

class Victim {
  final int totalCount;
  final int unconsciousCount;
  final bool hasHeavyBleeding;
  final bool hasBreathingDifficulty;
  final bool hasCriticalCondition;
  final bool hasVisibleInjury;
  final bool hasElderly;
  final bool hasChild;

  Victim({
    required this.totalCount,
    required this.unconsciousCount,
    required this.hasHeavyBleeding,
    required this.hasBreathingDifficulty,
    required this.hasCriticalCondition,
    required this.hasVisibleInjury,
    required this.hasElderly,
    required this.hasChild,
  });

  Map<String, dynamic> toJson() => {
        'total_count': totalCount,
        'unconscious_count': unconsciousCount,
        'has_heavy_bleeding': hasHeavyBleeding,
        'has_breathing_difficulty': hasBreathingDifficulty,
        'has_critical_condition': hasCriticalCondition,
        'has_visible_injury': hasVisibleInjury,
        'has_elderly': hasElderly,
        'has_child': hasChild,
      };
}

class EmergencyRequirement {
  final String resource;
  final int quantity;
  final bool required;
  final String priority; // REQUIRED, PREPARE, OPTIONAL
  bool isReady;

  EmergencyRequirement({
    required this.resource,
    required this.quantity,
    required this.required,
    required this.priority,
    this.isReady = false,
  });
}

class Ambulance {
  final String id;
  final String name;
  String status; // AVAILABLE, BUSY, EN_ROUTE
  final double latitude;
  final double longitude;
  final String capability; // ALS, BLS
  final List<String> equipment;
  final String driver;
  final double distanceKm;
  double score;

  Ambulance({
    required this.id,
    required this.name,
    required this.status,
    required this.latitude,
    required this.longitude,
    required this.capability,
    required this.equipment,
    required this.driver,
    required this.distanceKm,
    this.score = 0.0,
  });

  factory Ambulance.fromJson(Map<String, dynamic> json) {
    return Ambulance(
      id: json['id'],
      name: json['name'],
      status: json['status'],
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      capability: json['capability'],
      equipment: List<String>.from(json['equipment'] ?? []),
      driver: json['driver'] ?? '',
      distanceKm: (json['distance_km'] as num).toDouble(),
    );
  }
}

class Hospital {
  final String id;
  final String name;
  final String address;
  final double latitude;
  final double longitude;
  int bedsAvailable;
  int icuAvailable;
  final bool hasTrauma;
  final bool hasOxygen;
  final bool hasBloodBank;
  final bool hasVentilator;
  final bool hasOperationTheatre;
  final List<String> specialists;
  final String level;
  final double distanceKm;
  double score;
  String status; // NORMAL, PREPARING, READY

  Hospital({
    required this.id,
    required this.name,
    required this.address,
    required this.latitude,
    required this.longitude,
    required this.bedsAvailable,
    required this.icuAvailable,
    required this.hasTrauma,
    required this.hasOxygen,
    required this.hasBloodBank,
    required this.hasVentilator,
    required this.hasOperationTheatre,
    required this.specialists,
    required this.level,
    required this.distanceKm,
    this.score = 0.0,
    this.status = 'NORMAL',
  });

  factory Hospital.fromJson(Map<String, dynamic> json) {
    return Hospital(
      id: json['id'],
      name: json['name'],
      address: json['address'] ?? '',
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      bedsAvailable: json['beds_available'] ?? 0,
      icuAvailable: json['icu_available'] ?? 0,
      hasTrauma: json['has_trauma'] ?? false,
      hasOxygen: json['has_oxygen'] ?? false,
      hasBloodBank: json['has_blood_bank'] ?? false,
      hasVentilator: json['has_ventilator'] ?? false,
      hasOperationTheatre: json['has_operation_theatre'] ?? false,
      specialists: List<String>.from(json['specialists'] ?? []),
      level: json['level'] ?? 'Unknown',
      distanceKm: (json['distance_km'] as num).toDouble(),
    );
  }
}

class RouteNode {
  final String id;
  final String name;
  final double lat;
  final double lng;

  RouteNode({
    required this.id,
    required this.name,
    required this.lat,
    required this.lng,
  });
}

class EmergencyRoute {
  final String name;
  final List<String> nodes;
  final List<String> roads;
  final double totalKm;
  final int etaMinutes;
  bool isBlocked;

  EmergencyRoute({
    required this.name,
    required this.nodes,
    required this.roads,
    required this.totalKm,
    required this.etaMinutes,
    this.isBlocked = false,
  });
}

class CommunicationPacket {
  final String incidentId;
  final String severity;
  final int victims;
  final double latitude;
  final double longitude;
  final String ambulanceId;
  final String hospitalId;
  final String messageType;
  final DateTime timestamp;
  String deliveryStatus; // PENDING, SENT, RECEIVED, DELIVERED

  CommunicationPacket({
    required this.incidentId,
    required this.severity,
    required this.victims,
    required this.latitude,
    required this.longitude,
    required this.ambulanceId,
    required this.hospitalId,
    required this.messageType,
    required this.timestamp,
    this.deliveryStatus = 'PENDING',
  });

  Map<String, dynamic> toJson() => {
        'incidentId': incidentId,
        'severity': severity,
        'victims': victims,
        'latitude': latitude,
        'longitude': longitude,
        'ambulanceId': ambulanceId,
        'hospitalId': hospitalId,
        'messageType': messageType,
        'timestamp': timestamp.toIso8601String(),
      };
}

class TimelineEvent {
  final String event;
  final DateTime timestamp;
  final String? details;
  final String status; // INFO, SUCCESS, WARNING, ERROR

  TimelineEvent({
    required this.event,
    required this.timestamp,
    this.details,
    this.status = 'INFO',
  });
}

class VerifiedIncident {
  String incidentId;
  String status; // DETECTED, FUSED, VERIFIED, ASSESSED, REQUIREMENTS_PREDICTED,
  // AMBULANCE_MATCHED, HOSPITAL_MATCHED, HOSPITAL_PREPARING,
  // ROUTE_ACTIVE, PATIENT_ARRIVED, HANDOVER, CLOSED
  List<IncidentReport> reports;
  double latitude;
  double longitude;
  DateTime detectedAt;
  String? severity;
  Victim? victims;
  List<EmergencyRequirement> requirements;
  Ambulance? assignedAmbulance;
  Hospital? assignedHospital;
  EmergencyRoute? currentRoute;
  List<TimelineEvent> timeline;
  List<CommunicationPacket> communicationLog;
  String? ambulanceStatus; // ASSIGNED, EN_ROUTE_TO_ACCIDENT, ARRIVED, PICKED_UP, EN_ROUTE_TO_HOSPITAL, AT_HOSPITAL
  DateTime? etaToAccident;
  DateTime? etaToHospital;
  bool hospitalReady;

  VerifiedIncident({
    required this.incidentId,
    required this.status,
    required this.reports,
    required this.latitude,
    required this.longitude,
    required this.detectedAt,
    this.severity,
    this.victims,
    this.requirements = const [],
    this.assignedAmbulance,
    this.assignedHospital,
    this.currentRoute,
    this.timeline = const [],
    this.communicationLog = const [],
    this.ambulanceStatus,
    this.etaToAccident,
    this.etaToHospital,
    this.hospitalReady = false,
  });
}
