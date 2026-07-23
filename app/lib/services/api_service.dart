import 'dart:convert';
import 'package:http/http.dart' as http;

import '../models/consult_result.dart';

class ApiException implements Exception {
  final String message;
  ApiException(this.message);

  @override
  String toString() => message;
}

class ApiService {
  /// Base URL of the FastAPI backend (main.py / uvicorn).
  ///
  /// - Android emulator: 10.0.2.2 maps to the host machine's localhost.
  /// - iOS simulator: localhost works directly.
  /// - Physical phone: use your computer's LAN IP, e.g. http://192.168.1.42:8000
  ///   (phone and computer must be on the same Wi-Fi network).
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  Future<ConsultResult> consult({
    required String name,
    required String placeOfBirth,
    required String dateOfBirth,
    required String timeOfBirth,
    required String question,
  }) async {
    final uri = Uri.parse('$baseUrl/consult');

    late final http.Response response;
    try {
      response = await http
          .post(
            uri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'name': name,
              'place_of_birth': placeOfBirth,
              'date_of_birth': dateOfBirth,
              'time_of_birth': timeOfBirth,
              'question': question,
            }),
          )
          .timeout(const Duration(seconds: 60));
    } catch (_) {
      throw ApiException(
          'Could not reach the server at $baseUrl. Make sure the backend is running and reachable from this device.');
    }

    if (response.statusCode == 200) {
      return ConsultResult.fromJson(
          jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
    }

    String detail = 'Request failed (${response.statusCode}).';
    try {
      final body = jsonDecode(utf8.decode(response.bodyBytes));
      if (body is Map && body['detail'] != null) {
        detail = body['detail'].toString();
      }
    } catch (_) {
      // ignore parse errors, fall back to generic message
    }
    throw ApiException(detail);
  }
}
