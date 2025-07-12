import 'package:json_annotation/json_annotation.dart';

part 'checkin_model.g.dart';

@JsonSerializable()
class CheckinModel {
  final String id;
  final String userId;
  final String templeId;
  final String amuletId;
  final int pointsEarned;
  final DateTime checkinTime;
  final String? notes;
  final Map<String, dynamic>? metadata; // 額外資料，如GPS位置等

  CheckinModel({
    required this.id,
    required this.userId,
    required this.templeId,
    required this.amuletId,
    required this.pointsEarned,
    required this.checkinTime,
    this.notes,
    this.metadata,
  });

  factory CheckinModel.fromJson(Map<String, dynamic> json) =>
      _$CheckinModelFromJson(json);

  Map<String, dynamic> toJson() => _$CheckinModelToJson(this);

  CheckinModel copyWith({
    String? id,
    String? userId,
    String? templeId,
    String? amuletId,
    int? pointsEarned,
    DateTime? checkinTime,
    String? notes,
    Map<String, dynamic>? metadata,
  }) {
    return CheckinModel(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      templeId: templeId ?? this.templeId,
      amuletId: amuletId ?? this.amuletId,
      pointsEarned: pointsEarned ?? this.pointsEarned,
      checkinTime: checkinTime ?? this.checkinTime,
      notes: notes ?? this.notes,
      metadata: metadata ?? this.metadata,
    );
  }

  @override
  String toString() {
    return 'CheckinModel(id: $id, userId: $userId, templeId: $templeId, pointsEarned: $pointsEarned)';
  }
}
