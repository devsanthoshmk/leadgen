import { JSDOM } from 'jsdom';
import { parsePhoneNumberFromString } from 'libphonenumber-js';

export function extractPhone(text) {
  if (!text) return '';
  
  const phoneRegex = /(?:\+?\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}/g;
  const matches = text.match(phoneRegex);
  
  if (!matches) return '';

  for (const match of matches) {
    if (match.replace(/\D/g, '').length < 8) continue;

    const phoneNumber = parsePhoneNumberFromString(match, 'JP'); // Fallback region
    if (phoneNumber && phoneNumber.isValid()) {
      return phoneNumber.number;
    }
  }
  return '';
}

async function fetchit(url) {
  const headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
  };

  try {
    const response = await fetch(url, {
      headers,
      redirect: 'follow'
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const htmlText = await response.text();
    const dom = new JSDOM(htmlText);
    const doc = dom.window.document;

    const items = doc.querySelector('#search')?.querySelectorAll('.VkpGBb');
    if (!items) return []; 
    
    const scrapedData = [];

    items.forEach((item) => {
      const row = {
        title: 'N/A',
        stars: 0,
        reviews: 0,
        category: '',
        address: '',
        completePhoneNumber: '',
        url: ''
      };

      const titleEl = item.querySelector('[role="heading"]');
      if (titleEl) {
        row.title = titleEl.textContent.replace(/\s+/g, ' ').trim();
      }

      // --- 1. NEW STRATEGY: ADDRESS FROM DIRECTIONS URL ---
      const allLinks = Array.from(item.querySelectorAll('a'));
      const directionsLink = allLinks.find(a => a.getAttribute('href')?.startsWith('/maps/dir/'));
      
      if (directionsLink) {
        const href = directionsLink.getAttribute('href');
        try {
          // The URL format is /maps/dir//{Start}/{Destination}/data=...
          // We split by /data=, take the first half, and grab the very last segment separated by /
          const destSegment = href.split('/data=')[0].split('/').pop();
          
          if (destSegment) {
            let fullAddress = decodeURIComponent(destSegment).replace(/\+/g, ' ').trim();
            
            // Clean up: Google usually attaches the Title to the start or end of this string. Let's slice it out.
            if (row.title && row.title !== 'N/A') {
              if (fullAddress.startsWith(row.title)) {
                // Remove title from start, then strip any leading commas or spaces
                fullAddress = fullAddress.substring(row.title.length).replace(/^[, \-]+/, '').trim();
              } else if (fullAddress.endsWith(row.title)) {
                // Remove title from end, then strip any trailing commas or spaces
                fullAddress = fullAddress.substring(0, fullAddress.length - row.title.length).replace(/[, \-]+$/, '').trim();
              }
            }
            row.address = fullAddress;
          }
        } catch (e) {
          console.warn('Could not parse directions URL for address');
        }
      }

      // --- 2. WEBSITE EXTRACTION ---
      const websiteLink = allLinks.find(a => {
        const linkText = a.textContent.toLowerCase();
        return linkText.includes('website') && a.hasAttribute('href') && a.href.startsWith('http');
      });

      if (websiteLink) {
        row.url = websiteLink.href;
      }

      // --- 3. TEXT PARSING (Reviews, Category, Phone, and Address Fallback) ---
      const detailsDiv = item.querySelector('.rllt__details');
      if (detailsDiv) {
        const lines = Array.from(detailsDiv.children); 
        
        lines.forEach(line => {
          if (line.getAttribute('role') === 'heading' || line.querySelector('[role="heading"]')) return;

          const text = line.textContent.replace(/\s+/g, ' ').trim();
          if (!text) return;

          if (line.querySelector('[role="img"]') || text.match(/^\d\.\d/)) {
            const starSpan = line.querySelector('.yi40Hd') || line.querySelector('[aria-hidden="true"]');
            if (starSpan) row.stars = parseFloat(starSpan.textContent) || 0;
            
            const reviewSpan = line.querySelector('[aria-label*="reviews"]') || line.querySelector('.RDApEe');
            if (reviewSpan) row.reviews = parseInt(reviewSpan.textContent.replace(/\D/g, '')) || 0;
            
            if (text.includes('·')) {
              row.category = text.split('·').pop().trim();
            }
            return;
          }

          const isStatusOrFeature = text.includes('Opens') || text.includes('Closed') || 
                                    text.includes('Open 24 hours') || text.includes('Dine-in') || 
                                    text.includes('Takeout') || text.includes('Delivery');
          const isQuote = line.classList.contains('pJ3Ci');
          if (isStatusOrFeature || isQuote) return;

          const segments = text.split('·').map(s => s.trim());
          segments.forEach(segment => {
            if (segment.includes('years in business')) return;

            const phone = extractPhone(segment);
            const looksLikePhone = /^[\d\s\-\+\(\)]{8,}$/.test(segment);

            if (phone) {
              row.completePhoneNumber = phone;
            } else if (!looksLikePhone && segment.length > 3 && !row.address) {
              // Fallback: only set the address from text if the Directions link trick failed
              row.address = segment;
            }
          });
        });
      }

      scrapedData.push(row);
    });
    
    return scrapedData;
  } catch (error) {
    console.error('Error fetching data:', error);
    return [];
  }
}

export async function search(query) {
  const fullList = [];
  let pagination = 0;

  while (true) {
    const url = new URL('https://www.google.com/search');
    url.search = new URLSearchParams({
      q: query,
      start: pagination,
      udm: '1',
    }).toString();
    console.log(`Fetching: ${url}`);

    const result = await fetchit(url.toString());
    if (result?.length > 0) {
      pagination += 10;
      fullList.push(...result);
    } else {
      break;
    }
  }

  return Array.from(new Map(fullList.map(item => [item.title + item.address, item])).values());
}

// SAMPLE OUTPUT
// [
//   {
//     title: 'Anytime Fitness Shimbashi',
//     stars: 4.4,
//     reviews: 44385,
//     category: 'Gym',
//     address: 'Minato City, Tokyo, Japan',
//     completePhoneNumber: '+81364359145',
//     url: 'https://www.anytimefitness.co.jp/shimbashi/'
//   },
//   {
//     title: 'Club 360 Fitness and rehabilitation',
//     stars: 4.8,
//     reviews: 48227,
//     category: 'Gym',
//     address: 'Minato City, Tokyo, Japan',
//     completePhoneNumber: '+81364349667',
//     url: 'http://www.club360.jp/'
//   },
//   {
//     title: 'GYMS',
//     stars: 4.6,
//     reviews: 46442,
//     category: 'Gym',
//     address: 'Shibuya, Tokyo, Japan',
//     completePhoneNumber: '+81120634777',
//     url: 'https://www.p-gyms.jp/'
//   }.................
// ]