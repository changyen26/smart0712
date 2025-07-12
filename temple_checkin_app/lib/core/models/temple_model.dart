import 'package:json_annotation/json_annotation.dart';

part 'temple_model.g.dart';

@JsonSerializable()
class TempleModel {
  final String id;
  final String name;
  final String mainDeity; // 主祀神
  final String description;
  final String address;
  final double latitude;
  final double longitude;
  final String? imageUrl;
  final int blessingBonus; // 福報加成值
  final bool isActive;
  final DateTime createdAt;
  final DateTime? updatedAt;

  TempleModel({
    required this.id,
    required this.name,
    required this.mainDeity,
    required this.description,
    required this.address,
    required this.latitude,
    required this.longitude,
    this.imageUrl,
    this.blessingBonus = 1,
    this.isActive = true,
    required this.createdAt,
    this.updatedAt,
  });

  factory TempleModel.fromJson(Map<String, dynamic> json) =>
      _$TempleModelFromJson(json);

  Map<String, dynamic> toJson() => _$TempleModelToJson(this);

  TempleModel copyWith({
    String? id,
    String? name,
    String? mainDeity,
    String? description,
    String? address,
    double? latitude,
    double? longitude,
    String? imageUrl,
    int? blessingBonus,
    bool? isActive,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return TempleModel(
      id: id ?? this.id,
      name: name ?? this.name,
      mainDeity: mainDeity ?? this.mainDeity,
      description: description ?? this.description,
      address: address ?? this.address,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      imageUrl: imageUrl ?? this.imageUrl,
      blessingBonus: blessingBonus ?? this.blessingBonus,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'TempleModel(id: $id, name: $name, mainDeity: $mainDeity, blessingBonus: $blessingBonus)';
  }
}
