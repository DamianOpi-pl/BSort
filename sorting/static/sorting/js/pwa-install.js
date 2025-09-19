// PWA Installation Prompt Handler
class PWAInstaller {
    constructor() {
        this.deferredPrompt = null;
        this.installButton = null;
        this.init();
    }

    init() {
        // Listen for the beforeinstallprompt event
        window.addEventListener('beforeinstallprompt', (e) => {
            console.log('PWA: beforeinstallprompt event fired');
            // Prevent the mini-infobar from appearing on mobile
            e.preventDefault();
            // Store the event so it can be triggered later
            this.deferredPrompt = e;
            // Show the install button
            this.showInstallButton();
        });

        // Listen for the appinstalled event
        window.addEventListener('appinstalled', (e) => {
            console.log('PWA: App was installed');
            this.hideInstallButton();
            // Clear the deferredPrompt so it can be garbage collected
            this.deferredPrompt = null;
            // Show a success message
            this.showInstallSuccessMessage();
        });

        // Check if app is already installed
        this.checkIfInstalled();
        
        // Create install button
        this.createInstallButton();
    }

    createInstallButton() {
        // Create install button element
        this.installButton = document.createElement('button');
        this.installButton.id = 'pwa-install-btn';
        this.installButton.className = 'btn btn-outline-light btn-sm';
        this.installButton.innerHTML = '<i class="fas fa-download me-1"></i> Zainstaluj Aplikację';
        this.installButton.style.display = 'none';
        this.installButton.title = 'Zainstaluj BSort jako aplikację na swoim urządzeniu';

        // Add click handler
        this.installButton.addEventListener('click', () => {
            this.handleInstallClick();
        });

        // Add to topbar
        const userDropdown = document.querySelector('.topbar .dropdown');
        if (userDropdown) {
            userDropdown.parentNode.insertBefore(this.installButton, userDropdown);
        } else {
            // Fallback: add to the end of topbar
            const topbarRight = document.querySelector('.topbar .d-flex');
            if (topbarRight) {
                topbarRight.appendChild(this.installButton);
            }
        }
    }

    showInstallButton() {
        if (this.installButton && !this.isInstalled()) {
            this.installButton.style.display = 'inline-block';
            console.log('PWA: Install button shown');
        }
    }

    hideInstallButton() {
        if (this.installButton) {
            this.installButton.style.display = 'none';
            console.log('PWA: Install button hidden');
        }
    }

    async handleInstallClick() {
        if (!this.deferredPrompt) {
            console.log('PWA: No deferred prompt available');
            return;
        }

        // Show the install prompt
        this.deferredPrompt.prompt();
        
        // Wait for the user to respond to the prompt
        const { outcome } = await this.deferredPrompt.userChoice;
        
        if (outcome === 'accepted') {
            console.log('PWA: User accepted the install prompt');
        } else {
            console.log('PWA: User dismissed the install prompt');
        }
        
        // Clear the deferred prompt
        this.deferredPrompt = null;
        this.hideInstallButton();
    }

    checkIfInstalled() {
        // Check if running in standalone mode (iOS)
        const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
        
        // Check if running as PWA (Android)
        const isInWebAppiOS = window.navigator.standalone === true;
        
        // Check if running as PWA (general)
        const isInWebApp = window.matchMedia('(display-mode: standalone)').matches || 
                          window.navigator.standalone === true;

        if (isInWebApp) {
            console.log('PWA: App is running as installed PWA');
            this.hideInstallButton();
            this.addInstalledIndicator();
        }
    }

    isInstalled() {
        return window.matchMedia('(display-mode: standalone)').matches || 
               window.navigator.standalone === true;
    }

    addInstalledIndicator() {
        // Add a small indicator that the app is installed
        const brand = document.querySelector('.navbar-brand');
        if (brand && !brand.querySelector('.pwa-installed-badge')) {
            const badge = document.createElement('span');
            badge.className = 'badge bg-success ms-2 pwa-installed-badge';
            badge.style.fontSize = '0.6rem';
            badge.textContent = 'PWA';
            badge.title = 'Aplikacja zainstalowana';
            brand.appendChild(badge);
        }
    }

    showInstallSuccessMessage() {
        // Show a bootstrap alert for successful installation
        const container = document.querySelector('.container.mt-4');
        if (container) {
            const alert = document.createElement('div');
            alert.className = 'alert alert-success alert-dismissible fade show';
            alert.innerHTML = `
                <i class="fas fa-check-circle me-2"></i>
                BSort został pomyślnie zainstalowany jako aplikacja!
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            container.insertBefore(alert, container.firstChild);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 5000);
        }
    }
}

// Initialize PWA installer when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    new PWAInstaller();
});

// Add some basic offline detection
window.addEventListener('online', function() {
    console.log('PWA: Back online');
    // Remove any offline indicators
    const offlineIndicator = document.querySelector('.offline-indicator');
    if (offlineIndicator) {
        offlineIndicator.remove();
    }
});

window.addEventListener('offline', function() {
    console.log('PWA: Gone offline');
    // Show offline indicator
    const topbar = document.querySelector('.topbar');
    if (topbar && !document.querySelector('.offline-indicator')) {
        const indicator = document.createElement('div');
        indicator.className = 'offline-indicator bg-warning text-dark text-center py-1';
        indicator.innerHTML = '<i class="fas fa-wifi me-1"></i> Tryb offline - niektóre funkcje mogą być ograniczone';
        topbar.parentNode.insertBefore(indicator, topbar.nextSibling);
    }
});