# Quick Integration Guide: Face Recognition + Flutter

## System Overview

```
FLUTTER APP (Your Device)
       ↓
   [Camera Widget]
       ↓
   [FaceRecognitionApiService]
       ↓
FastAPI Backend (http://localhost:8000 or http://192.168.x.x:8000)
       ↓
   [Face Recognition Routes]
       ↓
MySQL Database (face_attendance)
```

## Step 1: Copy API Service to Flutter App

1. Open your Flutter project in Android Studio / VS Code
2. Copy `face_recognition_api_service.dart` to:
   ```
   lib/services/
   ```

3. Add dependency to `pubspec.yaml`:
   ```yaml
   dependencies:
     http: ^1.1.0
   ```

4. Run:
   ```bash
   flutter pub get
   ```

## Step 2: Update Backend URL

In `lib/services/face_recognition_api_service.dart`, change the base URL:

```dart
// For development (same machine)
static const String baseUrl = 'http://localhost:8000';

// For network access
static const String baseUrl = 'http://192.168.1.100:8000';
// Replace 192.168.1.100 with your Mini PC IP address
// Find it with: ipconfig (on Windows)
```

## Step 3: Update Your Screens

### Register Screen Example

```dart
import 'package:image_picker/image_picker.dart';
import 'dart:io';

class RegisterStudentScreen extends StatefulWidget {
  @override
  _RegisterStudentScreenState createState() => _RegisterStudentScreenState();
}

class _RegisterStudentScreenState extends State<RegisterStudentScreen> {
  final apiService = FaceRecognitionApiService();
  final _studentIdController = TextEditingController();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  File? _imageFile;
  bool _isLoading = false;

  Future<void> _takePicture() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.camera);
    
    if (pickedFile != null) {
      setState(() {
        _imageFile = File(pickedFile.path);
      });
    }
  }

  Future<void> _registerStudent() async {
    if (_imageFile == null || 
        _studentIdController.text.isEmpty ||
        _nameController.text.isEmpty ||
        _emailController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please fill all fields and take a photo')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final result = await apiService.registerStudent(
        studentId: _studentIdController.text,
        name: _nameController.text,
        parentEmail: _emailController.text,
        imageFile: _imageFile!,
      );

      if (result['status'] == 'success') {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(result['message'])),
        );
        _clear();
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.toString()}')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _clear() {
    _studentIdController.clear();
    _nameController.clear();
    _emailController.clear();
    setState(() => _imageFile = null);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Register Student')),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            // Display captured photo
            if (_imageFile != null)
              Image.file(_imageFile!, height: 200)
            else
              Container(
                height: 200,
                color: Colors.grey[300],
                child: Center(child: Text('No photo taken')),
              ),
            SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _takePicture,
              icon: Icon(Icons.camera),
              label: Text('Take Photo'),
            ),
            SizedBox(height: 16),
            TextField(
              controller: _studentIdController,
              decoration: InputDecoration(
                labelText: 'Student ID',
                hintText: 'e.g., S001',
              ),
            ),
            SizedBox(height: 16),
            TextField(
              controller: _nameController,
              decoration: InputDecoration(labelText: 'Student Name'),
            ),
            SizedBox(height: 16),
            TextField(
              controller: _emailController,
              decoration: InputDecoration(labelText: 'Parent Email'),
              keyboardType: TextInputType.emailAddress,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: _isLoading ? null : _registerStudent,
              child: _isLoading
                  ? CircularProgressIndicator()
                  : Text('Register Student'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _studentIdController.dispose();
    _nameController.dispose();
    _emailController.dispose();
    super.dispose();
  }
}
```

### Recognition Screen Example

```dart
class RecognitionScreen extends StatefulWidget {
  @override
  _RecognitionScreenState createState() => _RecognitionScreenState();
}

class _RecognitionScreenState extends State<RecognitionScreen> {
  final apiService = FaceRecognitionApiService();
  File? _imageFile;
  bool _isLoading = false;
  String _eventType = 'ENTRY';
  Map<String, dynamic>? _recognitionResult;

  Future<void> _takePicture() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.camera);
    
    if (pickedFile != null) {
      setState(() => _imageFile = File(pickedFile.path));
      await _recognize();
    }
  }

  Future<void> _recognize() async {
    if (_imageFile == null) return;

    setState(() => _isLoading = true);

    try {
      final result = await apiService.recognizeFace(
        imageFile: _imageFile!,
        eventType: _eventType,
        location: 'Main Gate',
      );

      setState(() => _recognitionResult = result);

      if (result['status'] == 'Recognized') {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${result['student']} - ${result['event']}'),
            backgroundColor: Colors.green,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Student not recognized'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.toString()}')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Face Recognition')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (_imageFile != null)
              Image.file(_imageFile!, height: 200)
            else
              Container(
                height: 200,
                color: Colors.grey[300],
                child: Center(child: Icon(Icons.image, size: 80)),
              ),
            SizedBox(height: 24),
            SegmentedButton<String>(
              segments: [
                ButtonSegment(value: 'ENTRY', label: Text('Entry')),
                ButtonSegment(value: 'EXIT', label: Text('Exit')),
              ],
              selected: {_eventType},
              onSelectionChanged: (Set<String> newSelection) {
                setState(() => _eventType = newSelection.first);
              },
            ),
            SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _isLoading ? null : _takePicture,
              icon: Icon(Icons.camera),
              label: Text(_isLoading ? 'Processing...' : 'Capture Face'),
            ),
            if (_recognitionResult != null) ...[
              SizedBox(height: 24),
              Card(
                margin: EdgeInsets.symmetric(horizontal: 16),
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    children: [
                      Text(
                        _recognitionResult!['status'],
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if (_recognitionResult!['status'] == 'Recognized') ...[
                        SizedBox(height: 8),
                        Text(
                          'Student: ${_recognitionResult!['student']}',
                        ),
                        Text(
                          'ID: ${_recognitionResult!['student_id']}',
                        ),
                        Text(
                          'Event: ${_recognitionResult!['event']}',
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
```

## Step 4: Add Required Dependencies

Update `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  image_picker: ^1.0.0
  camera: ^0.10.0
```

## Step 5: Add Camera Permissions

### Android (`android/app/src/main/AndroidManifest.xml`)

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.INTERNET" />
```

### iOS (`ios/Runner/Info.plist`)

```xml
<key>NSCameraUsageDescription</key>
<string>We need camera access to capture student photos</string>
<key>NSLocalNetworkUsageDescription</key>
<string>We need network access to communicate with the backend</string>
<key>NSBonjourServices</key>
<array>
  <string>_http._tcp</string>
</array>
```

## Step 6: Find Your Mini PC IP Address

### Windows (on Mini PC)
```powershell
ipconfig
```
Look for IPv4 Address (e.g., 192.168.1.100)

### Update Flutter App
```dart
static const String baseUrl = 'http://192.168.1.100:8000';
```

## Step 7: Test Integration

1. Start backend on Mini PC:
   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Update Flutter app with Mini PC IP

3. Test health check in your app:
   ```dart
   final apiService = FaceRecognitionApiService();
   final isConnected = await apiService.testConnection();
   print('Connected: $isConnected');
   ```

## Troubleshooting

### Connection Refused
- ✅ Backend is running on Mini PC
- ✅ Port 8000 is open
- ✅ IP address is correct
- ✅ Both devices are on same network

### CORS Error
- ✅ Backend CORS is configured for your Flutter app
- ✅ Check `allowed_origins` in `app/core/config.py`

### Image Upload Error
- ✅ Image file path is correct
- ✅ File permissions are set
- ✅ Image size is reasonable (< 5MB)

### Database Connection Error
- ✅ MySQL/XAMPP is running
- ✅ Database `face_attendance` exists
- ✅ Check `.env` credentials

## API Response Examples

### Successful Registration
```json
{
  "status": "success",
  "message": "Student registered successfully",
  "student_id": "S001"
}
```

### Successful Recognition
```json
{
  "status": "Recognized",
  "student": "John Doe",
  "student_id": "S001",
  "event": "ENTRY",
  "parent_email": "parent@example.com",
  "timestamp": "2026-03-05T10:30:00"
}
```

## Next Steps

1. ✅ Backend running
2. ✅ Flutter API service integrated
3. 🚀 Build your Flutter screens using the examples
4. 📱 Test on your device
5. 🎯 Deploy to production
