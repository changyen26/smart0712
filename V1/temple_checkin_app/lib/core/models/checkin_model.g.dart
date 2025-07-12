// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'checkin_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

CheckinModel _$CheckinModelFromJson(Map<String, dynamic> json) => CheckinModel(
      id: json['id'] as String,
      userId: json['userId'] as String,
      templeId: json['templeId'] as String,
      amuletId: json['amuletId'] as String,
      pointsEarned: (json['pointsEarned'] as num).toInt(),
      checkinTime: DateTime.parse(json['checkinTime'] as String),
      notes: json['notes'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$CheckinModelToJson(CheckinModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'userId': instance.userId,
      'templeId': instance.templeId,
      'amuletId': instance.amuletId,
      'pointsEarned': instance.pointsEarned,
      'checkinTime': instance.checkinTime.toIso8601String(),
      'notes': instance.notes,
      'metadata': instance.metadata,
    };
