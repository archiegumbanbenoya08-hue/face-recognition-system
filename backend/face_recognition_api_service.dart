import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';

class FaceRecognitionApiService {
  // Update this with your Mini PC IP address
  static const String baseUrl = 'http://localhost:8000';
  // For network access: 'http://192.168.x.x:8000'

  static const String apiPrefix = '/api/face';
  static const Duration timeout = Duration(seconds: 30);

  /// Register a new student with face image
  Future<Map<String, dynamic>> registerStudent({
    required String studentId,
    required String name,
    required String parentEmail,
    required File imageFile,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl$apiPrefix/register/');
      final request = http.MultipartRequest('POST', uri);

      request.fields['student_id'] = studentId;
      request.fields['name'] = name;
      request.fields['parent_email'] = parentEmail;
      request.files.add(
        await http.MultipartFile.fromPath('file', imageFile.path),
      );

      final response = await request.send().timeout(timeout);
      final responseBody = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return jsonDecode(responseBody);
      } else {
        throw Exception('Failed to register student: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Register student error: $e');
    }
  }

  /// Recognize a face for entry/exit
  Future<Map<String, dynamic>> recognizeFace({
    required File imageFile,
    required String eventType, // 'ENTRY' or 'EXIT'
    String location = 'Main Gate',
  }) async {
    try {
      final uri = Uri.parse(
        '$baseUrl$apiPrefix/recognize/$eventType',
      ).replace(queryParameters: {'location': location});
      final request = http.MultipartRequest('POST', uri);

      request.files.add(
        await http.MultipartFile.fromPath('file', imageFile.path),
      );

      final response = await request.send().timeout(timeout);
      final responseBody = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return jsonDecode(responseBody);
      } else {
        throw Exception('Recognition failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Recognition error: $e');
    }
  }

  /// Get all registered students
  Future<List<Map<String, dynamic>>> getAllStudents() async {
    try {
      final uri = Uri.parse('$baseUrl$apiPrefix/students/');
      final response = await http.get(uri).timeout(timeout);

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return List<Map<String, dynamic>>.from(data);
      } else {
        throw Exception('Failed to get students: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Get students error: $e');
    }
  }

  /// Get specific student details
  Future<Map<String, dynamic>> getStudent(String studentId) async {
    try {
      final uri = Uri.parse('$baseUrl$apiPrefix/student/$studentId');
      final response = await http.get(uri).timeout(timeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else if (response.statusCode == 404) {
        throw Exception('Student not found');
      } else {
        throw Exception('Failed to get student: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Get student error: $e');
    }
  }

  /// Get campus entry/exit logs
  Future<Map<String, dynamic>> getCampusLogs({
    String? studentId,
    int limit = 50,
  }) async {
    try {
      final queryParams = {'limit': limit.toString()};
      if (studentId != null) {
        queryParams['student_id'] = studentId;
      }

      final uri = Uri.parse(
        '$baseUrl$apiPrefix/campus-logs/',
      ).replace(queryParameters: queryParams);
      final response = await http.get(uri).timeout(timeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get logs: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Get logs error: $e');
    }
  }

  /// Get campus logs for a specific student with filters
  Future<List<Map<String, dynamic>>> getStudentLogs({
    required String studentId,
    int limit = 50,
  }) async {
    try {
      final data = await getCampusLogs(studentId: studentId, limit: limit);
      final logs = data['logs'] as List<dynamic>;
      return List<Map<String, dynamic>>.from(logs);
    } catch (e) {
      throw Exception('Get student logs error: $e');
    }
  }

  /// Check backend health
  Future<Map<String, dynamic>> healthCheck() async {
    try {
      final uri = Uri.parse('$baseUrl/health');
      final response = await http.get(uri).timeout(timeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Health check failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Health check error: $e');
    }
  }

  /// Test connection to backend
  Future<bool> testConnection() async {
    try {
      await healthCheck();
      return true;
    } catch (e) {
      return false;
    }
  }
}
