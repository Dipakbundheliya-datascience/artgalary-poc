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
        // Add instruction message first (centered)
        addInstructionMessage();

        // Then add the greeting message (left-aligned)
        const response = await fetch(`${API_URL}/greeting`);
        const data = await response.json();

        addMessage('assistant', data.message);
    } catch (error) {
        console.error('Error initializing chat:', error);
        showError('Failed to connect to the server. Please make sure the backend is running.');
    }
}

function addInstructionMessage() {
    const chatContainer = document.getElementById('chatContainer');

    // Define categories from the artworks data
    const categories = [
        'Renaissance', 'Baroque', 'Romanticism', 'Impressionism',
        'Post-Impressionism', 'Landscape', 'Portrait', 'Genre Painting',
        'History Painting', 'Religious', 'Rococo', 'Mannerism',
        'Modernism', 'Miniature Art'
    ];

    // Define available colors
    const colors = [
        'Blue', 'Red', 'Green', 'Gold', 'White', 'Brown',
        'Beige', 'Black', 'Gray', 'Pink', 'Yellow', 'Purple',
        'Orange', 'Turquoise', 'Ochre', 'Olive'
    ];

    const instructionDiv = document.createElement('div');
    instructionDiv.className = 'instruction-message';
    instructionDiv.innerHTML = `
        <h3>Welcome to MoodMatch AI Art Gallery</h3>

        <div class="instruction-section">
            <h4>
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                Available Art Categories
            </h4>
            <div class="instruction-tags">
                ${categories.map(cat => `<span class="instruction-tag">${cat}</span>`).join('')}
            </div>
        </div>

        <div class="instruction-section">
            <h4>
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"></path>
                </svg>
                Available Colors
            </h4>
            <div class="instruction-tags">
                ${colors.map(color => `<span class="instruction-tag">${color}</span>`).join('')}
            </div>
        </div>

        <div class="instruction-section">
            <h4>
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Price Range
            </h4>
            <div class="price-range">₹1.8 Lakh - ₹6.8 Lakh</div>
        </div>
    `;

    chatContainer.appendChild(instructionDiv);
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

        // Format period as "Since YEAR"
        const periodFormatted = artwork.period ? formatPeriod(artwork.period) : '';

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
                ${periodFormatted ? `<div>${periodFormatted}</div>` : ''}
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

// Function to format period as "Since YEAR"
function formatPeriod(period) {
    if (!period) return '';

    // Extract year from period string (handles formats like "1865", "ca. 1835", "1570s", "1290–1300")
    const yearMatch = period.match(/(\d{4})/);
    if (yearMatch) {
        const year = yearMatch[1];
        return `Since ${year}`;
    }
    return period; // Return as-is if no year found
}

// Export artworks to PDF
async function exportToPDF(artworks) {
    // Show loading message
    const chatContainer = document.getElementById('chatContainer');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant';
    loadingDiv.id = 'pdf-loading';
    loadingDiv.innerHTML = '<div class="message-content">Generating PDF with all images... This may take a moment. (0/' + artworks.length + ' images loaded)</div>';
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Helper function to update loading message
    const updateLoadingMessage = (loaded, total) => {
        const loadingMsg = document.getElementById('pdf-loading');
        if (loadingMsg) {
            loadingMsg.innerHTML = `<div class="message-content">Generating PDF with all images... (${loaded}/${total} images loaded)</div>`;
        }
    };

    try {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF('p', 'mm', 'a4');

        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        const margin = 20;

        // Function to get image as base64 via backend proxy with retry logic
        const getBase64Image = async (url, retries = 3) => {
            for (let attempt = 1; attempt <= retries; attempt++) {
                try {
                    console.log(`Fetching image via backend proxy (attempt ${attempt}/${retries}):`, url);

                    // Use backend proxy endpoint to avoid CORS issues
                    const proxyUrl = `${API_URL}/proxy-image?url=${encodeURIComponent(url)}`;

                    const response = await fetch(proxyUrl);

                    if (!response.ok) {
                        throw new Error(`Proxy request failed: ${response.status}`);
                    }

                    const data = await response.json();

                    if (data.success && data.data_url) {
                        console.log('✓ Successfully loaded image via proxy:', url);
                        return data.data_url;
                    } else {
                        console.error('Proxy returned unsuccessful response:', data);
                        if (attempt < retries) {
                            console.log(`Retrying... (${attempt + 1}/${retries})`);
                            await new Promise(resolve => setTimeout(resolve, 1000 * attempt)); // Exponential backoff
                            continue;
                        }
                        return null;
                    }
                } catch (error) {
                    console.error(`Error loading image via proxy (attempt ${attempt}/${retries}):`, url, error);
                    if (attempt < retries) {
                        console.log(`Retrying... (${attempt + 1}/${retries})`);
                        await new Promise(resolve => setTimeout(resolve, 1000 * attempt)); // Exponential backoff
                    } else {
                        return null;
                    }
                }
            }
            return null;
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
                    updateLoadingMessage(imagesLoaded + imagesFailed, artworks.length);
                    console.log(`✓ Image ${i + 1} loaded successfully`);
                } else {
                    console.warn(`✗ Image ${i + 1} failed to load`);
                    imagesFailed++;
                    updateLoadingMessage(imagesLoaded + imagesFailed, artworks.length);
                    yPosition += 5;
                }
            } catch (error) {
                console.error('Error adding image to PDF:', error);
                imagesFailed++;
                updateLoadingMessage(imagesLoaded + imagesFailed, artworks.length);
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

            // Period formatted as "Since YEAR"
            if (artwork.period) {
                pdf.setTextColor(100, 100, 100);
                pdf.setFont(undefined, 'normal');
                const periodText = formatPeriod(artwork.period);
                pdf.text(periodText, margin, yPosition);
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