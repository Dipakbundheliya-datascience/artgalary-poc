const API_URL = 'http://localhost:8000';
let conversationHistory = [];
let currentArtworks = [];

// Initialize chat on page load
window.addEventListener('DOMContentLoaded', async () => {
    await initChat();

    // Enter key to send message
    document.getElementById('userInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});

async function initChat() {
    try {
        const response = await fetch(`${API_URL}/greeting`);
        const data = await response.json();

        addMessage('assistant', data.message);
    } catch (error) {
        console.error('Error initializing chat:', error);
        showError('Failed to connect to the server. Please make sure the backend is running.');
    }
}

function addMessage(role, content) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formatMessage(content);

    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function formatMessage(content) {
    // Convert markdown-style bold
    content = content.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Convert line breaks
    content = content.replace(/\n/g, '<br>');

    return content;
}

function addArtworkCards(artworks) {
    const chatContainer = document.getElementById('chatContainer');

    // Store artworks for export
    currentArtworks = artworks;

    artworks.forEach((artwork, index) => {
        const card = document.createElement('div');
        card.className = 'artwork-card';

        const priceFormatted = new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(artwork.price);

        // Calculate age for period
        const periodWithAge = artwork.period ? artwork.period + calculateArtworkAge(artwork.period) : '';

        card.innerHTML = `
            <img src="${artwork.image_url}"
                 alt="${artwork.title}"
                 onclick="window.open('${artwork.image_url}', '_blank')"
                 onerror="this.src='https://via.placeholder.com/400x300?text=Image+Not+Available'">
            <div class="artwork-title">${artwork.title}</div>
            ${artwork.artist ? `<div style="font-size: 15px; color: #64748b; margin-bottom: 8px; font-style: italic;">by ${artwork.artist}</div>` : ''}
            <div class="artwork-price">${priceFormatted}</div>
            <div class="artwork-info">
                <div><strong>Medium:</strong> ${artwork.medium}</div>
                ${artwork.dimensions ? `<div><strong>Dimensions:</strong> ${artwork.dimensions}</div>` : ''}
                ${periodWithAge ? `<div><strong>Period:</strong> ${periodWithAge}</div>` : ''}
                <div style="margin-top: 12px;">
                    <strong>Style:</strong><br>
                    ${artwork.style.map(s => `<span class="badge style">${s}</span>`).join('')}
                </div>
                <div style="margin-top: 8px;">
                    <strong>Colors:</strong><br>
                    ${artwork.colors.map(c => `<span class="badge color">${c}</span>`).join('')}
                </div>
                <div style="margin-top: 8px;">
                    <strong>Mood:</strong><br>
                    ${artwork.mood.map(m => `<span class="badge mood">${m}</span>`).join('')}
                </div>
            </div>
        `;

        chatContainer.appendChild(card);
    });

    // Add export button after all artwork cards
    const exportBtn = document.createElement('button');
    exportBtn.className = 'export-btn';
    exportBtn.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
        </svg>
        Export to PDF
    `;
    exportBtn.onclick = () => exportToPDF(artworks);
    exportBtn.style.marginLeft = '0';
    exportBtn.style.marginBottom = '20px';
    chatContainer.appendChild(exportBtn);

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTyping() {
    document.getElementById('typingIndicator').classList.add('active');
}

function hideTyping() {
    document.getElementById('typingIndicator').classList.remove('active');
}

function showError(message) {
    const chatContainer = document.getElementById('chatContainer');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    chatContainer.appendChild(errorDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const message = input.value.trim();

    if (!message) return;

    // Disable input
    input.disabled = true;
    sendBtn.disabled = true;

    // Add user message to UI
    addMessage('user', message);

    // Add to conversation history
    conversationHistory.push({
        role: 'user',
        content: message
    });

    // Clear input
    input.value = '';

    // Show typing indicator
    showTyping();

    try {
        // Send to backend
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                messages: conversationHistory
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Hide typing indicator
        hideTyping();

        // Add assistant message
        addMessage('assistant', data.message);

        // Add to conversation history
        conversationHistory.push({
            role: 'assistant',
            content: data.message
        });

        // If recommendations, show artwork cards
        if (data.type === 'recommendation' && data.artworks) {
            addArtworkCards(data.artworks);
        }

    } catch (error) {
        hideTyping();
        console.error('Error sending message:', error);
        showError('Sorry, something went wrong. Please try again.');
    } finally {
        // Re-enable input
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

// Function to calculate age from period
function calculateArtworkAge(period) {
    if (!period) return '';

    // Extract year from period string (handles formats like "1865", "ca. 1835", "1570s", "1290–1300")
    const yearMatch = period.match(/(\d{4})/);
    if (yearMatch) {
        const year = parseInt(yearMatch[1]);
        const currentYear = new Date().getFullYear();
        const age = currentYear - year;
        return ` (${age} years old)`;
    }
    return '';
}

// Export artworks to PDF
async function exportToPDF(artworks) {
    // Show loading message
    const chatContainer = document.getElementById('chatContainer');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant';
    loadingDiv.id = 'pdf-loading';
    loadingDiv.innerHTML = '<div class="message-content">Generating PDF with all images... This may take a moment.</div>';
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    try {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF('p', 'mm', 'a4');

        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        const margin = 20;

        // Function to get image as base64 via backend proxy
        const getBase64Image = async (url) => {
            try {
                console.log('Fetching image via backend proxy:', url);

                // Use backend proxy endpoint to avoid CORS issues
                const proxyUrl = `${API_URL}/proxy-image?url=${encodeURIComponent(url)}`;

                const response = await fetch(proxyUrl);

                if (!response.ok) {
                    throw new Error(`Proxy request failed: ${response.status}`);
                }

                const data = await response.json();

                if (data.success && data.data_url) {
                    console.log('Successfully loaded image via proxy:', url);
                    return data.data_url;
                } else {
                    console.error('Proxy returned unsuccessful response:', data);
                    return null;
                }
            } catch (error) {
                console.error('Error loading image via proxy:', url, error);
                return null;
            }
        };

        // Add cover page
        let yPosition = pageHeight / 2 - 30;
        pdf.setFontSize(28);
        pdf.setTextColor(124, 58, 237);
        const title = 'MoodMatch AI';
        const titleWidth = pdf.getTextWidth(title);
        pdf.text(title, (pageWidth - titleWidth) / 2, yPosition);

        yPosition += 12;
        pdf.setFontSize(16);
        pdf.setTextColor(100, 100, 100);
        const subtitle = 'Artwork Recommendations';
        const subtitleWidth = pdf.getTextWidth(subtitle);
        pdf.text(subtitle, (pageWidth - subtitleWidth) / 2, yPosition);

        yPosition += 15;
        pdf.setFontSize(12);
        const date = `Generated on: ${new Date().toLocaleDateString()}`;
        const dateWidth = pdf.getTextWidth(date);
        pdf.text(date, (pageWidth - dateWidth) / 2, yPosition);

        // Process each artwork on a separate page
        let imagesLoaded = 0;
        let imagesFailed = 0;
        
        for (let i = 0; i < artworks.length; i++) {
            const artwork = artworks[i];

            // Add new page for each artwork
            pdf.addPage();
            yPosition = margin;

            // Add artwork title
            pdf.setFontSize(18);
            pdf.setTextColor(124, 58, 237);
            const titleLines = pdf.splitTextToSize(artwork.title, pageWidth - 2 * margin);
            pdf.text(titleLines, margin, yPosition);
            yPosition += 8 * titleLines.length;

            // Add artist
            if (artwork.artist) {
                pdf.setFontSize(13);
                pdf.setTextColor(100, 116, 139);
                pdf.setFont(undefined, 'italic');
                const artistLines = pdf.splitTextToSize(`by ${artwork.artist}`, pageWidth - 2 * margin);
                pdf.text(artistLines, margin, yPosition);
                pdf.setFont(undefined, 'normal');
                yPosition += 7 * artistLines.length;
            }

            yPosition += 5;

            // Add image - load each image individually
            try {
                console.log(`Loading image ${i + 1}/${artworks.length}:`, artwork.image_url);
                const imgData = await getBase64Image(artwork.image_url);
                if (imgData) {
                    const imgWidth = pageWidth - 2 * margin;
                    const imgHeight = 100; // Increased height for better visibility

                    pdf.addImage(imgData, 'JPEG', margin, yPosition, imgWidth, imgHeight);
                    yPosition += imgHeight + 10;
                    imagesLoaded++;
                    console.log(`✓ Image ${i + 1} loaded successfully`);
                } else {
                    console.warn(`✗ Image ${i + 1} failed to load`);
                    imagesFailed++;
                    yPosition += 5;
                }
            } catch (error) {
                console.error('Error adding image to PDF:', error);
                imagesFailed++;
                yPosition += 5;
            }

            // Add price
            const priceFormatted = new Intl.NumberFormat('en-IN', {
                style: 'currency',
                currency: 'INR',
                maximumFractionDigits: 0
            }).format(artwork.price);

            pdf.setFontSize(16);
            pdf.setTextColor(20, 184, 166);
            pdf.text(priceFormatted, margin, yPosition);
            yPosition += 10;

            // Add metadata
            pdf.setFontSize(11);
            pdf.setTextColor(50, 50, 50);

            // Medium
            pdf.setFont(undefined, 'bold');
            pdf.text('Medium: ', margin, yPosition);
            pdf.setFont(undefined, 'normal');
            pdf.setTextColor(100, 100, 100);
            const mediumLines = pdf.splitTextToSize(artwork.medium, pageWidth - margin * 2 - 20);
            pdf.text(mediumLines, margin + 22, yPosition);
            yPosition += 6 * mediumLines.length;

            // Dimensions
            if (artwork.dimensions) {
                pdf.setTextColor(50, 50, 50);
                pdf.setFont(undefined, 'bold');
                pdf.text('Dimensions: ', margin, yPosition);
                pdf.setFont(undefined, 'normal');
                pdf.setTextColor(100, 100, 100);
                const dimText = pdf.splitTextToSize(artwork.dimensions, pageWidth - margin * 2 - 28);
                pdf.text(dimText, margin + 28, yPosition);
                yPosition += 6 * dimText.length;
            }

            // Period with age calculation
            if (artwork.period) {
                pdf.setTextColor(50, 50, 50);
                pdf.setFont(undefined, 'bold');
                pdf.text('Period: ', margin, yPosition);
                pdf.setFont(undefined, 'normal');
                pdf.setTextColor(100, 100, 100);
                const ageText = calculateArtworkAge(artwork.period);
                pdf.text(artwork.period + ageText, margin + 18, yPosition);
                yPosition += 6;
            }

            // Style
            if (artwork.style && artwork.style.length > 0) {
                pdf.setTextColor(50, 50, 50);
                pdf.setFont(undefined, 'bold');
                pdf.text('Style: ', margin, yPosition);
                pdf.setFont(undefined, 'normal');
                pdf.setTextColor(100, 100, 100);
                const styleText = pdf.splitTextToSize(artwork.style.join(', '), pageWidth - margin * 2 - 16);
                pdf.text(styleText, margin + 16, yPosition);
                yPosition += 6 * styleText.length;
            }

            // Colors
            if (artwork.colors && artwork.colors.length > 0) {
                pdf.setTextColor(50, 50, 50);
                pdf.setFont(undefined, 'bold');
                pdf.text('Colors: ', margin, yPosition);
                pdf.setFont(undefined, 'normal');
                pdf.setTextColor(100, 100, 100);
                const colorsText = pdf.splitTextToSize(artwork.colors.join(', '), pageWidth - margin * 2 - 18);
                pdf.text(colorsText, margin + 18, yPosition);
                yPosition += 6 * colorsText.length;
            }

            // Mood
            if (artwork.mood && artwork.mood.length > 0) {
                pdf.setTextColor(50, 50, 50);
                pdf.setFont(undefined, 'bold');
                pdf.text('Mood: ', margin, yPosition);
                pdf.setFont(undefined, 'normal');
                pdf.setTextColor(100, 100, 100);
                const moodText = pdf.splitTextToSize(artwork.mood.join(', '), pageWidth - margin * 2 - 16);
                pdf.text(moodText, margin + 16, yPosition);
                yPosition += 6 * moodText.length;
            }

            // Add page number at bottom
            pdf.setFontSize(9);
            pdf.setTextColor(150, 150, 150);
            pdf.text(`Page ${i + 2} of ${artworks.length + 1}`, pageWidth / 2, pageHeight - 10, { align: 'center' });
        }

        // Save the PDF
        pdf.save('MoodMatch-AI-Artworks.pdf');

        // Remove loading message
        const loadingMsg = document.getElementById('pdf-loading');
        if (loadingMsg) {
            loadingMsg.remove();
        }

        // Show success message with statistics
        const successDiv = document.createElement('div');
        successDiv.className = 'message assistant';
        const statsMessage = imagesFailed > 0 
            ? `PDF exported successfully! ${imagesLoaded} of ${artworks.length} images loaded. ${imagesFailed} image(s) could not be loaded due to CORS restrictions.`
            : `PDF exported successfully with all ${imagesLoaded} artwork images!`;
        successDiv.innerHTML = `<div class="message-content">${statsMessage}</div>`;
        chatContainer.appendChild(successDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        console.log(`PDF Export Complete - Images loaded: ${imagesLoaded}, Failed: ${imagesFailed}`);

    } catch (error) {
        console.error('Error generating PDF:', error);

        // Remove loading message
        const loadingMsg = document.getElementById('pdf-loading');
        if (loadingMsg) {
            loadingMsg.remove();
        }

        showError('Failed to generate PDF. Please try again.');
    }
}