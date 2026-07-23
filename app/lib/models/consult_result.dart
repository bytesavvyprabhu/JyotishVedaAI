class Ascendant {
  final double longitude;
  final String sign;

  Ascendant({required this.longitude, required this.sign});

  factory Ascendant.fromJson(Map<String, dynamic> json) {
    return Ascendant(
      longitude: (json['longitude'] as num).toDouble(),
      sign: json['sign'] as String,
    );
  }
}

class PlanetPosition {
  final String name;
  final double longitude;
  final String sign;
  final int house;
  final String nakshatra;
  final int pada;

  PlanetPosition({
    required this.name,
    required this.longitude,
    required this.sign,
    required this.house,
    required this.nakshatra,
    required this.pada,
  });

  factory PlanetPosition.fromJson(String name, Map<String, dynamic> json) {
    return PlanetPosition(
      name: name,
      longitude: (json['longitude'] as num).toDouble(),
      sign: json['sign'] as String,
      house: json['house'] as int,
      nakshatra: json['nakshatra'] as String,
      pada: json['pada'] as int,
    );
  }
}

class DashaPeriod {
  final String lord;
  final double start;
  final double end;
  final bool current;

  DashaPeriod({
    required this.lord,
    required this.start,
    required this.end,
    required this.current,
  });

  factory DashaPeriod.fromJson(Map<String, dynamic> json) {
    return DashaPeriod(
      lord: json['lord'] as String,
      start: (json['start'] as num).toDouble(),
      end: (json['end'] as num).toDouble(),
      current: json['current'] as bool? ?? false,
    );
  }
}

class BirthChart {
  final Ascendant ascendant;
  final List<PlanetPosition> planets;
  final String moonSign;
  final List<DashaPeriod> mahadasha;

  BirthChart({
    required this.ascendant,
    required this.planets,
    required this.moonSign,
    required this.mahadasha,
  });

  factory BirthChart.fromJson(Map<String, dynamic> json) {
    final planetsJson = json['planets'] as Map<String, dynamic>? ?? {};
    return BirthChart(
      ascendant: Ascendant.fromJson(json['ascendant'] as Map<String, dynamic>),
      planets: planetsJson.entries
          .map((e) => PlanetPosition.fromJson(e.key, e.value as Map<String, dynamic>))
          .toList(),
      moonSign: json['moon_sign'] as String? ?? '',
      mahadasha: (json['mahadasha'] as List<dynamic>? ?? [])
          .map((e) => DashaPeriod.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

class ConsultResult {
  final String name;
  final BirthChart chart;
  final String answer;

  ConsultResult({required this.name, required this.chart, required this.answer});

  factory ConsultResult.fromJson(Map<String, dynamic> json) {
    return ConsultResult(
      name: json['name'] as String,
      chart: BirthChart.fromJson(json['chart'] as Map<String, dynamic>),
      answer: json['answer'] as String,
    );
  }
}
