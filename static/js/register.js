let video = document.getElementById('video');
let canvas = document.getElementById('canvas');
let captureBtn = document.getElementById('captureBtn');
let startCamera = document.getElementById('startCamera');
let retakeBtn = document.getElementById('retakeBtn');
let submitBtn = document.getElementById('submitBtn');
let preview = document.getElementById('preview');
let capturedImage = document.getElementById('capturedImage');
let messageDiv = document.getElementById('message');
let stream = null;
let capturedData = null;

startCamera.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 } 
        });
        video.srcObject = stream;
        captureBtn.disabled = false;
        startCamera.disabled = true;
        showMessage('Camera started successfully', 'success');
    } catch (err) {
        showMessage('Error accessing camera: ' + err.message, 'error');
    }
});

captureBtn.addEventListener('click', () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    let context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    capturedData = canvas.toDataURL('image/jpeg');
    capturedImage.src = capturedData;
    preview.style.display = 'block';
    
    captureBtn.style.display = 'none';
    retakeBtn.style.display = 'inline-block';
    submitBtn.disabled = false;
    
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
    }
    
    showMessage('Photo captured! Please fill in all details and submit.', 'success');
});

retakeBtn.addEventListener('click', () => {
    preview.style.display = 'none';
    capturedData = null;
    captureBtn.style.display = 'inline-block';
    retakeBtn.style.display = 'none';
    submitBtn.disabled = true;
    startCamera.disabled = false;
    showMessage('', '');
});

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!capturedData) {
        showMessage('Please capture a photo first', 'error');
        return;
    }
    
    let empId = document.getElementById('emp_id').value;
    let name = document.getElementById('name').value;
    let email = document.getElementById('email').value;
    let department = document.getElementById('department').value;
    
    submitBtn.disabled = true;
    showMessage('Processing registration...', 'info');
    
    try {
        let response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                emp_id: empId,
                name: name,
                email: email,
                department: department,
                image: capturedData
            })
        });
        
        let data = await response.json();
        
        if (data.success) {
            showMessage(data.message + ' Redirecting to home...', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        } else {
            showMessage(data.message, 'error');
            submitBtn.disabled = false;
        }
    } catch (err) {
        showMessage('Error: ' + err.message, 'error');
        submitBtn.disabled = false;
    }
});

function showMessage(msg, type) {
    messageDiv.textContent = msg;
    messageDiv.className = 'message ' + type;
    if (!msg) {
        messageDiv.style.display = 'none';
    }
}
