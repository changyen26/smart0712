import 'package:json_annotation/json_annotation.dart';

part 'amulet_model.g.dart';

@JsonSerializable()
class AmuletModel {
  final String id;
  final String userId;
  final String uid; // NFC UID
  final String name;
  final String? description;
  final String? imageUrl;
  final bool isActive;
  final DateTime createdAt;
  final DateTime? updatedAt;

  AmuletModel({
    required this.id,
    required this.userId,
    required this.uid,
    required this.name,
    this.description,
    this.imageUrl,
    this.isActive = true,
    required this.createdAt,
    this.updatedAt,
  });

  factory AmuletModel.fromJson(Map<String, dynamic> json) =>
      _$AmuletModelFromJson(json);

  Map<String, dynamic> toJson() => _$AmuletModelToJson(this);

  AmuletModel copyWith({
    String? id,
    String? userId,
    String? uid,
    String? name,
    String? description,
    String? imageUrl,
    bool? isActive,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return AmuletModel(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      uid: uid ?? this.uid,
      name: name ?? this.name,
      description: description ?? this.description,
      imageUrl: imageUrl ?? this.imageUrl,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'AmuletModel(id: $id, userId: $userId, uid: $uid, name: $name, isActive: $isActive)';
  }
}
