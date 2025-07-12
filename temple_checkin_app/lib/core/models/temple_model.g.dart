// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'temple_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

TempleModel _$TempleModelFromJson(Map<String, dynamic> json) => TempleModel(
      id: json['id'] as String,
      name: json['name'] as String,
      mainDeity: json['mainDeity'] as String,
      description: json['description'] as String,
      address: json['address'] as String,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      imageUrl: json['imageUrl'] as String?,
      blessingBonus: (json['blessingBonus'] as num?)?.toInt() ?? 1,
      isActive: json['isActive'] as bool? ?? true,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: json['updatedAt'] == null
          ? null
          : DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$TempleModelToJson(TempleModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'mainDeity': instance.mainDeity,
      'description': instance.description,
      'address': instance.address,
      'latitude': instance.latitude,
      'longitude': instance.longitude,
      'imageUrl': instance.imageUrl,
      'blessingBonus': instance.blessingBonus,
      'isActive': instance.isActive,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt?.toIso8601String(),
    };
