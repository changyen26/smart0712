// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'amulet_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AmuletModel _$AmuletModelFromJson(Map<String, dynamic> json) => AmuletModel(
      id: json['id'] as String,
      userId: json['userId'] as String,
      uid: json['uid'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      imageUrl: json['imageUrl'] as String?,
      isActive: json['isActive'] as bool? ?? true,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: json['updatedAt'] == null
          ? null
          : DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$AmuletModelToJson(AmuletModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'userId': instance.userId,
      'uid': instance.uid,
      'name': instance.name,
      'description': instance.description,
      'imageUrl': instance.imageUrl,
      'isActive': instance.isActive,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt?.toIso8601String(),
    };
