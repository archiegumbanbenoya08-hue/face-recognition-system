#!/usr/bin/env python3
"""
System Test & Verification Script
Checks all components before student registration
"""

import os
import sys
import importlib


def print_header(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def test_python_version():
    """Check Python version"""
    print_header("Python Version Check")
    
    version = sys.version_info
    required = (3, 8)
    
    print(f"Installed: Python {version.major}.{version.minor}.{version.micro}")
    
    if (version.major, version.minor) >= required:
        print(f"✓ Python {required[0]}.{required[1]}+ available")
        return True
    else:
        print(f"✗ Requires Python {required[0]}.{required[1]}+")
        return False


def test_dependencies():
    """Check all required libraries"""
    print_header("Dependency Check")
    
    dependencies = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'mysql': 'mysql-connector-python',
    }
    
    optional = {
        'face_recognition': 'face_recognition',
        'tensorflow': 'tensorflow',
    }
    
    all_good = True
    
    # Required dependencies
    print("\nRequired Libraries:")
    for module, package in dependencies.items():
        try:
            importlib.import_module(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED")
            print(f"    Install: pip install {package}")
            all_good = False
    
    # Optional dependencies
    print("\nOptional Libraries (for best performance):")
    optional_available = 0
    for module, package in optional.items():
        try:
            importlib.import_module(module)
            print(f"  ✓ {package}")
            optional_available += 1
        except ImportError:
            print(f"  ○ {package} - not installed")
            print(f"    Install: pip install {package}")
    
    if optional_available > 0:
        print(f"\n  {optional_available}/{len(optional)} optional libraries available")
    
    return all_good


def test_cascade_file():
    """Check Haar Cascade file"""
    print_header("Cascade File Check")
    
    cascade_path = "haarcascade_frontalface_default.xml"
    
    if os.path.exists(cascade_path):
        size = os.path.getsize(cascade_path)
        print(f"✓ Found: {cascade_path}")
        print(f"  Size: {size} bytes")
        return True
    else:
        print(f"✗ Missing: {cascade_path}")
        print("\n  Download from:")
        print("  https://github.com/opencv/opencv/blob/master/data/haarcascades/")
        print("  haarcascade_frontalface_default.xml")
        print(f"\n  Save to: {os.path.abspath(cascade_path)}")
        return False


def test_modules():
    """Check custom modules"""
    print_header("Custom Modules Check")
    
    modules = {
        'database': 'Database operations',
        'camera': 'Camera & face detection',
        'encoding': 'Face encoding',
        'registration': 'Registration workflow',
    }
    
    all_good = True
    for module, description in modules.items():
        try:
            importlib.import_module(module)
            print(f"✓ {module}.py - {description}")
        except Exception as e:
            print(f"✗ {module}.py - ERROR: {e}")
            all_good = False
    
    return all_good


def test_camera():
    """Test camera access"""
    print_header("Camera Access Check")
    
    try:
        import cv2
        print("Testing camera access...")
        
        # Try opening camera with multiple backends
        backends = [
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_MSMF, "Media Foundation"),
            (cv2.CAP_ANY, "Default"),
        ]
        
        camera_found = False
        for backend, name in backends:
            cap = cv2.VideoCapture(0, backend)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    print(f"✓ Camera accessible via {name}")
                    print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
                    camera_found = True
                    break
        
        if not camera_found:
            print("✗ Camera not accessible")
            print("\n  Troubleshooting:")
            print("  1. Check if camera is physically connected")
            print("  2. Close other apps using camera (Zoom, Teams, etc.)")
            print("  3. Check camera permissions in Windows Settings")
            print("  4. Try different USB port (if external)")
            print("  5. Update camera drivers")
        
        return camera_found
    
    except Exception as e:
        print(f"✗ Error testing camera: {e}")
        return False


def test_database():
    """Test database connection"""
    print_header("Database Connection Check")
    
    try:
        from database import get_connection, create_tables
        
        print("Connecting to MySQL...")
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check connection
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"✓ Connected to MySQL {version}")
        
        cursor.close()
        conn.close()
        
        # Test table creation
        print("\nCreating database tables...")
        create_tables()
        print("✓ Tables created/verified")
        
        return True
    
    except Exception as e:
        print(f"✗ Database error: {e}")
        print("\n  Troubleshooting:")
        print("  1. Start MySQL server (XAMPP Control Panel)")
        print("  2. Verify credentials in database.py")
        print("  3. Create database: CREATE DATABASE face_recognition_system;")
        return False


def test_folders():
    """Check required folders"""
    print_header("Directory Structure Check")
    
    folders = ['dataset', 'student_images']
    
    all_good = True
    for folder in folders:
        if os.path.exists(folder):
            print(f"✓ {folder}/ exists")
        else:
            print(f"○ {folder}/ will be created during registration")
            os.makedirs(folder, exist_ok=True)
    
    return all_good


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print(" Face Registration System - Pre-Flight Check")
    print("="*60)
    
    results = {
        'Python Version': test_python_version(),
        'Dependencies': test_dependencies(),
        'Cascade File': test_cascade_file(),
        'Custom Modules': test_modules(),
        'Camera': test_camera(),
        'Database': test_database(),
        'Folders': test_folders(),
    }
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test_name}")
    
    print(f"\nResult: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 System is ready for registration!")
        print("\nRun: python registration.py")
        return 0
    else:
        print("\n⚠ Some checks failed. See above for fixes.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
