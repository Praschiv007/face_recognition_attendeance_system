let video = document.getElementById('video');
let canvas = document.getElementById('canvas');
let startDetection = document.getElementById('startDetection');
let stopDetection = document.getElementById('stopDetection');
let messageDiv = document.getElementById('message');
let employeeInfo = document.getElementById('employeeInfo');
let detectionStatus = document.getElementById('detectionStatus');
let stream = null;
let detectionInterval = null;
let isProcessing = false;
let recentlyMarked = new Set();

const DETECTION_INTERVAL = 2000;
const COOLDOWN_PERIOD = 30000;

startDetection.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 } 
        });
        video.srcObject = stream;
        
        startDetection.style.display = 'none';
        stopDetection.style.display = 'inline-block';
        
        showMessage('Camera active. Automatic face detection started...', 'info');
        updateStatus('Scanning for faces...', 'active');
        
        detectionInterval = setInterval(detectAndRecognizeFace, DETECTION_INTERVAL);
        
    } catch (err) {
        showMessage('Error accessing camera: ' + err.message, 'error');
        updateStatus('Error', 'error');
    }
});

stopDetection.addEventListener('click', () => {
    stopFaceDetection();
    showMessage('Face detection stopped', 'info');
    updateStatus('Inactive', 'inactive');
});

function stopFaceDetection() {
    if (detectionInterval) {
        clearInterval(detectionInterval);
        detectionInterval = null;
    }
    
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        stream = null;
    }
    
    startDetection.style.display = 'inline-block';
    stopDetection.style.display = 'none';
    isProcessing = false;
}

async function detectAndRecognizeFace() {
    if (isProcessing || !stream) {
        return;
    }
    
    isProcessing = true;
    
    try {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        if (canvas.width === 0 || canvas.height === 0) {
            isProcessing = false;
            return;
        }
        
        let context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        let capturedData = canvas.toDataURL('image/jpeg', 0.8);
        
        updateStatus('Analyzing face...', 'processing');
        
        let response = await fetch('/api/mark_attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: capturedData
            })
        });
        
        let data = await response.json();
        
        if (data.success) {
            let empId = data.employee.emp_id;
            
            if (!recentlyMarked.has(empId)) {
                showMessage('✓ ' + data.message, 'success');
                
                document.getElementById('infoEmpId').textContent = data.employee.emp_id;
                document.getElementById('infoName').textContent = data.employee.name;
                document.getElementById('infoDept').textContent = data.employee.department || '-';
                document.getElementById('infoTime').textContent = new Date().toLocaleString();
                employeeInfo.style.display = 'block';
                
                recentlyMarked.add(empId);
                
                updateStatus('Face recognized: ' + data.employee.name, 'success');
                
                setTimeout(() => {
                    employeeInfo.style.display = 'none';
                    updateStatus('Scanning for faces...', 'active');
                }, 5000);
                
                setTimeout(() => {
                    recentlyMarked.delete(empId);
                }, COOLDOWN_PERIOD);
                
            } else {
                updateStatus('Already marked: ' + data.employee.name, 'cooldown');
            }
        } else {
            if (data.message.includes('No face detected')) {
                updateStatus('No face detected', 'warning');
            } else if (data.message.includes('not recognized')) {
                updateStatus('Face not recognized', 'warning');
                showMessage('Face detected but not recognized. Please register first.', 'error');
            } else {
                updateStatus('Scanning...', 'active');
            }
        }
    } catch (err) {
        console.error('Detection error:', err);
        updateStatus('Error during detection', 'error');
    } finally {
        isProcessing = false;
    }
}

function updateStatus(text, status) {
    if (detectionStatus) {
        detectionStatus.textContent = text;
        detectionStatus.className = 'detection-status status-' + status;
    }
}

function showMessage(msg, type) {
    messageDiv.textContent = msg;
    messageDiv.className = 'message ' + type;
    if (!msg) {
        messageDiv.style.display = 'none';
    }
}

window.addEventListener('beforeunload', () => {
    stopFaceDetection();
});
