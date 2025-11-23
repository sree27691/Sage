// content.js
// Extracts DOM and Images from the active page

function extractPageData() {
    try {
        const domHtml = document.documentElement.outerHTML;
        const images = Array.from(document.querySelectorAll('img'))
            .map(img => img.src)
            .filter(src => src.startsWith('http'))
            .slice(0, 10); // Limit to 10 images

        // Helper to find content by header keywords
        function extractSection(keywords, maxLength = 3000) {
            try {
                // Strategy 1: Look for headers
                const headerSelectors = [
                    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                    'strong', 'b',
                    'span', 'div',
                    '[class*="title"]', '[class*="heading"]', '[class*="label"]',
                    '[class*="Title"]', '[class*="Heading"]'
                ];

                const headers = Array.from(document.querySelectorAll(headerSelectors.join(', ')));

                for (const header of headers) {
                    const text = header.textContent?.toLowerCase() || '';
                    if (keywords.some(k => text.includes(k))) {
                        console.log(`[CONTENT.JS] Found header for keywords ${keywords}:`, header.textContent.slice(0, 50));

                        let content = "";

                        // Try to get next siblings
                        let sibling = header.nextElementSibling;
                        let attempts = 0;
                        while (sibling && attempts < 10 && content.length < maxLength) {
                            const siblingText = sibling.innerText || sibling.textContent || '';
                            if (siblingText.trim()) {
                                content += siblingText + "\n";
                            }
                            sibling = sibling.nextElementSibling;
                            attempts++;
                        }

                        // If we didn't get much, try parent container
                        if (content.length < 100) {
                            let parent = header.parentElement;
                            let parentAttempts = 0;
                            while (parent && parentAttempts < 3) {
                                const parentText = parent.innerText || parent.textContent || '';
                                if (parentText.length > content.length && parentText.length < maxLength * 2) {
                                    content = parentText;
                                    break;
                                }
                                parent = parent.parentElement;
                                parentAttempts++;
                            }
                        }

                        if (content.trim().length > 50) {
                            console.log(`[CONTENT.JS] Extracted ${content.length} chars for ${keywords[0]}`);
                            return content.slice(0, maxLength);
                        }
                    }
                }

                // Strategy 2: Look for containers with class names matching keywords
                for (const keyword of keywords) {
                    const cleanKeyword = keyword.replace(/[^a-z]/g, '');
                    const containers = document.querySelectorAll(`[class*="${cleanKeyword}"], [id*="${cleanKeyword}"]`);

                    for (const container of containers) {
                        const containerText = container.innerText || container.textContent || '';
                        if (containerText.length > 100 && containerText.length < maxLength * 2) {
                            console.log(`[CONTENT.JS] Found container for ${keyword}:`, container.className);
                            return containerText.slice(0, maxLength);
                        }
                    }
                }

            } catch (e) {
                console.error('[CONTENT.JS] Error extracting section:', e);
            }
            return null;
        }

        // Helper to extract reviews with more aggressive search
        function extractReviews() {
            try {
                // Try multiple selectors for reviews
                const reviewSelectors = [
                    '[data-hook="review"]',
                    '.review',
                    '[class*="review-item"]',
                    '[class*="customer-review"]',
                    '[id*="reviews"]'
                ];

                let reviews = [];
                for (const selector of reviewSelectors) {
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        reviews = Array.from(elements).slice(0, 10).map(el =>
                            (el.innerText || el.textContent || '').slice(0, 500)
                        );
                        break;
                    }
                }

                return reviews.length > 0 ? reviews.join('\n---\n') : null;
            } catch (e) {
                console.error('Error extracting reviews:', e);
                return null;
            }
        }

        const structuredContent = {
            // Product description & features
            "about_item": extractSection([
                "about this item",
                "about this product",
                "product overview",
                "feature bullets",
                "features",
                "key features",
                "product features",
                "highlights"
            ], 4000),

            // Technical specifications
            "technical_details": extractSection([
                "technical details",
                "technical specifications",
                "tech specs",
                "product information",
                "specifications",
                "spec sheet",
                "product specs",
                "details",
                "product details"
            ], 4000),

            // Customer reviews
            "reviews": extractReviews() || extractSection([
                "customer reviews",
                "top reviews",
                "reviews",
                "customer ratings",
                "what customers say",
                "verified purchase reviews"
            ], 5000),

            // What's included
            "whats_in_box": extractSection([
                "what's in the box",
                "what's included",
                "included components",
                "package contents",
                "in the box",
                "box contents"
            ], 2000),

            // Manufacturer info
            "manufacturer": extractSection([
                "from the manufacturer",
                "product description",
                "manufacturer description",
                "brand story",
                "about the brand"
            ], 3000),

            // Additional details
            "additional_info": extractSection([
                "additional information",
                "product information",
                "more details",
                "other details",
                "warranty",
                "warranty information"
            ], 2000),

            // Dimensions & weight
            "dimensions": extractSection([
                "dimensions",
                "product dimensions",
                "size",
                "weight",
                "package dimensions"
            ], 1000)
        };

        console.log('[CONTENT.JS] Extracted structured content:', {
            about_item: structuredContent.about_item ? 'Found' : 'Not found',
            technical_details: structuredContent.technical_details ? 'Found' : 'Not found',
            reviews: structuredContent.reviews ? 'Found' : 'Not found',
            whats_in_box: structuredContent.whats_in_box ? 'Found' : 'Not found',
            manufacturer: structuredContent.manufacturer ? 'Found' : 'Not found',
            additional_info: structuredContent.additional_info ? 'Found' : 'Not found',
            dimensions: structuredContent.dimensions ? 'Found' : 'Not found'
        });

        // Log actual content preview
        console.log('[CONTENT.JS] Content preview:');
        for (const [key, value] of Object.entries(structuredContent)) {
            if (value) {
                console.log(`  ${key}:`, value.slice(0, 200) + '...');
            }
        }

        return {
            url: window.location.href,
            dom_html: domHtml,
            images: images,
            structured_content: structuredContent,
            extension_version: "1.3"
        };
    } catch (error) {
        console.error('[CONTENT.JS] Error in extractPageData:', error);
        // Return minimal data to prevent complete failure
        return {
            url: window.location.href,
            dom_html: document.documentElement.outerHTML,
            images: [],
            structured_content: {},
            extension_version: "1.3"
        };
    }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "getPageData") {
        const data = extractPageData();
        sendResponse(data);
    }
    return true; // Important: keeps the message channel open for async response
});
