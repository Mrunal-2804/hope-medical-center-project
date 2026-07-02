/**
 * Frontend JavaScript for the Medical Website
 * Handles form submissions to the Python backend.
 */

// 1. Run initialization tasks as soon as the page loads
window.onload = async function() {
    // A. Run a connection test to ensure Flask backend is reachable
    try {
        const response = await fetch('http://127.0.0.1:5000/api/status');
        const data = await response.json();
        console.log("Backend Connection Status:", data.message);
    } catch (error) {
        console.error("Could not connect to Python backend:", error);
    }
    
    // B. Attach an event listener to the appointment booking form (index.html)
    const appointmentForm = document.getElementById('bookingForm');
    if (appointmentForm) {
        appointmentForm.addEventListener('submit', handleFormSubmit);
    }

    // C. Attach an event listener to the registration account form (register.html)
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegisterSubmit);
    }
};

// 2. This function captures your appointment form data and sends it to Python
async function handleFormSubmit(event) {
    event.preventDefault(); // Prevents the page from refreshing

    const formData = {
        fullName: document.getElementById('fullName')?.value || "",
        email: document.getElementById('email')?.value || "",
        phone: document.getElementById('phone')?.value || "",
        department: document.getElementById('department')?.value || "",
        dateTime: document.getElementById('dateTime')?.value || "",
        notes: document.getElementById('notes')?.value || "None Provided"
    };

    try {
        const response = await fetch('http://127.0.0.1:5000/api/book-appointment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (result.status === "success") {
            alert("Appointment booked successfully via Python Backend!");
        } else {
            alert("Error: " + result.message);
        }
    } catch (error) {
        console.error("Error submitting form:", error);
        alert("Failed to connect to the backend server.");
    }
}

// 3. This function captures your account registration data and sends it to Python
async function handleRegisterSubmit(event) {
    event.preventDefault(); // Stop standard page refreshing

    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const confirmPassword = document.getElementById('regConfirmPassword').value;
    
    const errorBox = document.getElementById('regErrorMessage');
    const successBox = document.getElementById('regSuccessMessage');

    // Reset alert visibility status
    errorBox.classList.add('hidden');
    successBox.classList.add('hidden');
    if (errorBox) errorBox.style.display = "none";
    if (successBox) successBox.style.display = "none";

    // Client-side Password verification check
    if (password !== confirmPassword) {
        errorBox.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> Passwords do not match!`;
        errorBox.classList.remove('hidden');
        errorBox.style.display = "block";
        return;
    }

    const payload = { name, email, password };

    try {
        // Broadcast data payload to Flask backend endpoint
        const response = await fetch('http://127.0.0.1:5000/api/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok && result.status === "success") {
            successBox.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${result.message}`;
            successBox.classList.remove('hidden');
            successBox.style.display = "block";
            document.getElementById('registerForm').reset();
            
            // Redirect smoothly straight back to your main landing index page after a 1.5 - 2 second delay
            setTimeout(() => { 
                window.location.href = 'index.html'; 
            }, 1500);
        } else {
            errorBox.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> ${result.message || 'Registration failed.'}`;
            errorBox.classList.remove('hidden');
            errorBox.style.display = "block";
        }
    } catch (error) {
        console.error("Connection Error:", error);
        errorBox.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> Failed to communicate with the Python database server.`;
        errorBox.classList.remove('hidden');
        errorBox.style.display = "block";
    }
}