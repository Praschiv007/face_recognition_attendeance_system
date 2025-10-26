let video = document.getElementById('video');
let canvas = document.getElementById('canvas');
let markAttendance = document.getElementById('markAttendance');
let startCamera = document.getElementById('startCamera');
let preview = document.getElementById('preview');
let capturedImage = document.getElementById('capturedImage');
let messageDiv = document.getElementById('message');
let employeeInfo = document.getElementById('employeeInfo');
let stream = null;

startCamera.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 } 
        });
        video.srcObject = stream;
        markAttendance.disabled = false;
        startCamera.disabled = true;
        showMessage('Camera started. Position your face and click "Mark Attendance"', 'info');
    } catch (err) {
        showMessage('Error accessing camera: ' + err.message, 'error');
    }
});

markAttendance.addEventListener('click', async () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    let context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    let capturedData = canvas.toDataURL('image/jpeg');
    capturedImage.src = capturedData;
    preview.style.display = 'block';
    
    markAttendance.disabled = true;
    showMessage('Recognizing face...', 'info');
    
    try {
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
            showMessage(data.message, 'success');
            
            document.getElementById('infoEmpId').textContent = data.employee.emp_id;
            document.getElementById('infoName').textContent = data.employee.name;
            document.getElementById('infoDept').textContent = data.employee.department || '-';
            document.getElementById('infoTime').textContent = new Date().toLocaleString();
            employeeInfo.style.display = 'block';
            
            setTimeout(() => {
                employeeInfo.style.display = 'none';
                preview.style.display = 'none';
                markAttendance.disabled = false;
            }, 5000);
        } else {
            showMessage(data.message, 'error');
            markAttendance.disabled = false;
        }
    } catch (err) {
        showMessage('Error: ' + err.message, 'error');
        markAttendance.disabled = false;
    }
});

function showMessage(msg, type) {
    messageDiv.textContent = msg;
    messageDiv.className = 'message ' + type;
    if (!msg) {
        messageDiv.style.display = 'none';
    }
}
