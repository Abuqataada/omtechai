document.addEventListener("DOMContentLoaded", () => {
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileNav = document.querySelector('.mobile-nav');

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', () => {
            mobileMenuToggle.classList.toggle('active');
            mobileNav.classList.toggle('active');
        });
    }
    
    // Scroll animations
    const elements = document.querySelectorAll(".highlight");
    const reveal = () => {
        const windowHeight = window.innerHeight;
        elements.forEach(el => {
            const top = el.getBoundingClientRect().top;
            if (top < windowHeight - 100) {
                el.classList.add("show");
            }
        });
    };
    
    window.addEventListener("scroll", reveal);
    reveal();
    
    // Header scroll effect
    const header = document.querySelector('header');
    let lastScrollY = window.scrollY;
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            header.style.background = 'rgba(16, 24, 43, 0.95)';
            header.style.backdropFilter = 'blur(10px)';
        } else {
            header.style.background = 'var(--bg-light)';
            header.style.backdropFilter = 'none';
        }
        
        lastScrollY = window.scrollY;
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                if (mobileNav.classList.contains('active')) {
                    mobileMenuToggle.classList.remove('active');
                    mobileNav.classList.remove('active');
                }
            }
        });
    });
});




// Main JavaScript for AI Exam Grader
// File upload progress (for future enhancement)
function showUploadProgress(fileInput) {
    const file = fileInput.files[0];
    if (file) {
        const progressDiv = document.createElement('div');
        progressDiv.className = 'progress mt-2';
        progressDiv.innerHTML = `
            <div class="progress-bar" role="progressbar" style="width: 0%"></div>
        `;
        fileInput.parentNode.appendChild(progressDiv);
        
        // Simulate upload progress (replace with actual upload logic)
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10;
            progressDiv.querySelector('.progress-bar').style.width = progress + '%';
            
            if (progress >= 100) {
                clearInterval(interval);
                progressDiv.remove();
            }
        }, 100);
    }
}

// Auto-dismiss alerts
setTimeout(() => {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}, 5000);

// Export functionality
function exportToCSV(data, filename) {
    const csvContent = "data:text/csv;charset=utf-8," + data;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Camera functionality placeholder
function initializeCamera() {
    // This would be implemented when camera feature is added
    console.log('Camera feature placeholder');
}