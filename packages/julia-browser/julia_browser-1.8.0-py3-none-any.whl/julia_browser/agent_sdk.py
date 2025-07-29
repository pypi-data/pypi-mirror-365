"""
AI Agent SDK - Simple website interaction functions for AI agents
Clean, direct functions matching CLI browser commands
"""

from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime

try:
    from .browser.engine import BrowserEngine
except ImportError:
    from browser.engine import BrowserEngine


class AgentSDK:
    """
    Simple AI Agent SDK for Julia Browser
    Provides direct website interaction functions like CLI commands
    """
    
    def __init__(self, user_agent: str = None, timeout: int = 30):
        """
        Initialize Agent SDK
        
        Args:
            user_agent: Custom user agent string
            timeout: Default timeout for requests
        """
        self.engine = BrowserEngine(user_agent)
        self.current_url = None
        self.current_soup = None
        self.form_data = {}
        self.default_timeout = timeout
        
    def open_website(self, url: str) -> Dict[str, Any]:
        """
        Open a website
        
        Args:
            url: Website URL to open
            
        Returns:
            Dict with success status and page info
        """
        try:
            success, content, soup = self.engine.fetch_page(url, timeout=self.default_timeout)
            
            if not success:
                return {'success': False, 'error': content}
            
            self.current_url = url
            self.current_soup = soup
            self.form_data = {}
            
            # Execute JavaScript if available
            if soup:
                js_content = self.engine.extract_javascript(soup)
                if js_content:
                    js_output = self.engine.js_engine.execute_script(js_content, soup)
                    if js_output.get('dom_updates'):
                        self.engine.apply_dom_updates(soup, js_output['dom_updates'])
            
            # Get basic page info
            title = soup.title.get_text() if soup.title else "No title"
            markdown = self.engine.render_page(soup)
            
            # Extract only meaningful text content (no markdown, HTML, or technical elements)
            clean_content = self._extract_text_only_content(soup)
            
            return {
                'success': True,
                'url': url,
                'title': title,
                'content': clean_content,
                'page_title': title
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_elements(self) -> Dict[str, Any]:
        """
        List all interactive elements on page (like CLI 'elements' command)
        
        Returns:
            Dict with numbered buttons, inputs, and links
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        try:
            from .browser.interactive_forms import InteractiveFormsHandler
            forms_handler = InteractiveFormsHandler(self.engine)
            forms_handler.extract_interactive_elements(self.current_soup, self.current_url)
            
            # Get buttons with numbers
            buttons = []
            button_num = 1
            
            for form in forms_handler.current_forms:
                for btn in form.get('buttons', []):
                    buttons.append({
                        'number': button_num,
                        'text': btn['text'],
                        'type': btn['type']
                    })
                    button_num += 1
            
            # Add standalone buttons and links
            standalone = self.current_soup.find_all(['button', 'a'])
            for elem in standalone:
                if elem.name == 'button':
                    buttons.append({
                        'number': button_num,
                        'text': elem.get_text(strip=True) or 'Button',
                        'type': 'button'
                    })
                    button_num += 1
                elif elem.name == 'a' and elem.get('href'):
                    buttons.append({
                        'number': button_num,
                        'text': elem.get_text(strip=True) or 'Link',
                        'type': 'link'
                    })
                    button_num += 1
            
            # Get input fields with numbers
            inputs = []
            input_num = 1
            
            for form in forms_handler.current_forms:
                for inp in form.get('inputs', []):
                    inputs.append({
                        'number': input_num,
                        'name': inp['name'],
                        'type': inp['type'],
                        'placeholder': inp.get('placeholder', '')
                    })
                    input_num += 1
            
            # Create clean text summary for users
            element_summary = self._create_element_summary(buttons, inputs)
            
            return {
                'success': True,
                'summary': element_summary,
                'buttons': buttons,
                'inputs': inputs,
                'total_elements': len(buttons) + len(inputs)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def click_element(self, element_number: int) -> Dict[str, Any]:
        """
        Click an element by its number (like CLI 'click' command)
        
        Args:
            element_number: Number of element to click
            
        Returns:
            Dict with click result
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        try:
            elements = self.list_elements()
            if not elements['success']:
                return elements
            
            # Find the element to click
            target = None
            for btn in elements['buttons']:
                if btn['number'] == element_number:
                    target = btn
                    break
            
            if not target:
                return {'success': False, 'error': f'Element {element_number} not found'}
            
            # Handle different click types
            if target['type'] == 'link':
                # Find and follow the link
                links = self.current_soup.find_all('a', href=True)
                for link in links:
                    if link.get_text(strip=True) == target['text']:
                        href = link.get('href')
                        new_url = urljoin(self.current_url, href)
                        result = self.open_website(new_url)
                        if result['success']:
                            result['message'] = f"Followed '{target['text']}' link to {result['title']}"
                        return result
                        
            elif target['type'] == 'submit':
                # Submit form
                return self.submit_form()
                
            else:
                # Regular button click
                return {
                    'success': True, 
                    'message': f"Clicked '{target['text']}' button successfully",
                    'action': 'clicked', 
                    'element': target['text']
                }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def type_text(self, field_number: int, text: str) -> Dict[str, Any]:
        """
        Type text into an input field by number (like CLI 'type' command)
        
        Args:
            field_number: Number of input field (starting from 1)
            text: Text to type
            
        Returns:
            Dict with typing result
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        try:
            elements = self.list_elements()
            if not elements['success']:
                return elements
            
            inputs = elements['inputs']
            if field_number > len(inputs) or field_number < 1:
                return {'success': False, 'error': f'Input field {field_number} not found. Found {len(inputs)} fields.'}
            
            target_input = inputs[field_number - 1]
            field_name = target_input['name'] or f'field_{field_number}'
            
            # Store typed data for form submission
            self.form_data[field_name] = text
            
            return {
                'success': True,
                'message': f"Typed '{text}' into {field_name} field",
                'action': 'typed',
                'field': field_name,
                'text': text,
                'field_number': field_number
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def submit_form(self) -> Dict[str, Any]:
        """
        Submit the current form (like CLI form submission)
        
        Returns:
            Dict with submission result
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        try:
            form = self.current_soup.find('form')
            if not form:
                return {'success': False, 'error': 'No form found on page'}
            
            action = form.get('action', '')
            method = form.get('method', 'GET').upper()
            
            # Resolve form action URL
            if not action:
                submit_url = self.current_url
            elif action.startswith('//'):
                parsed = urlparse(self.current_url)
                submit_url = f"{parsed.scheme}:{action}"
            elif action.startswith('/'):
                parsed = urlparse(self.current_url)
                submit_url = f"{parsed.scheme}://{parsed.netloc}{action}"
            elif action.startswith('http'):
                submit_url = action
            else:
                submit_url = urljoin(self.current_url, action)
            
            # Collect form data
            form_data = dict(self.form_data)
            
            # Add default form values
            for input_elem in form.find_all(['input', 'textarea', 'select']):
                name = input_elem.get('name')
                if name and name not in form_data:
                    value = input_elem.get('value', '')
                    if input_elem.name == 'textarea':
                        value = input_elem.get_text()
                    form_data[name] = value
            
            # Submit form
            if method == 'POST':
                response = self.engine.session.post(submit_url, data=form_data, timeout=self.default_timeout)
            else:
                response = self.engine.session.get(submit_url, params=form_data, timeout=self.default_timeout)
            
            if response.status_code == 200:
                # Update current page
                soup = BeautifulSoup(response.text, 'html.parser')
                self.current_soup = soup
                self.current_url = response.url
                
                # Clear form data
                self.form_data = {}
                
                # Render new page
                markdown = self.engine.render_page(soup)
                title = soup.title.get_text() if soup.title else "No title"
                
                return {
                    'success': True,
                    'action': 'form_submitted',
                    'url': response.url,
                    'title': title,
                    'content': markdown,
                    'page_title': title,
                    'markdown': markdown
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.reason}'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def follow_link(self, link_number: int) -> Dict[str, Any]:
        """
        Follow a link by number (like CLI link following)
        
        Args:
            link_number: Number of link to follow
            
        Returns:
            Dict with navigation result
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        try:
            # Get all links
            links = self.current_soup.find_all('a', href=True)
            if link_number > len(links) or link_number < 1:
                return {'success': False, 'error': f'Link {link_number} not found. Found {len(links)} links.'}
            
            target_link = links[link_number - 1]
            href = target_link.get('href')
            new_url = urljoin(self.current_url, href)
            
            return self.open_website(new_url)
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def search_page(self, search_term: str) -> Dict[str, Any]:
        """
        Search for text on current page with context
        
        Args:
            search_term: Text to search for
            
        Returns:
            Dict with search results and context
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        try:
            # Search in all text elements
            matches = []
            search_term_lower = search_term.lower()
            
            # Find all text elements and search within them
            for element in self.current_soup.find_all(text=True):
                text = element.strip()
                if text and search_term_lower in text.lower():
                    # Get context around the match
                    start_idx = text.lower().find(search_term_lower)
                    context_start = max(0, start_idx - 50)
                    context_end = min(len(text), start_idx + len(search_term) + 50)
                    context = text[context_start:context_end].strip()
                    
                    matches.append({
                        'text': text,
                        'context': context,
                        'parent_tag': element.parent.name if element.parent else None
                    })
            
            return {
                'success': True,
                'search_term': search_term,
                'matches': matches[:10],  # Limit to first 10 matches
                'total_matches': len(matches),
                'found': len(matches) > 0
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_page_info(self) -> Dict[str, Any]:
        """
        Get current page information
        
        Returns:
            Dict with page title, URL, content, and element counts
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        try:
            title = self.current_soup.title.get_text() if self.current_soup.title else "No title"
            markdown = self.engine.render_page(self.current_soup)
            
            # Count elements
            forms = len(self.current_soup.find_all('form'))
            buttons = len(self.current_soup.find_all(['button', 'input[type="button"]', 'input[type="submit"]']))
            inputs = len(self.current_soup.find_all('input'))
            links = len(self.current_soup.find_all('a', href=True))
            
            # Get meta description
            meta_desc = ""
            meta_tag = self.current_soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_desc = meta_tag.get('content', '')
            
            # Count words
            word_count = len(self.current_soup.get_text().split())
            
            # Check for JavaScript
            has_javascript = bool(self.current_soup.find_all('script'))
            
            return {
                'success': True,
                'title': title,
                'url': self.current_url,
                'content': markdown,
                'page_title': title,
                'markdown': markdown,
                'meta_description': meta_desc,
                'word_count': word_count,
                'element_counts': {
                    'forms': forms,
                    'buttons': buttons,
                    'inputs': inputs,
                    'links': links
                },
                'has_javascript': has_javascript,
                'has_forms': forms > 0,
                'is_interactive': buttons > 0 or inputs > 0 or forms > 0
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def follow_link(self, link_url: str) -> Dict[str, Any]:
        """
        Follow a link by URL (alternative to follow_link_number)
        
        Args:
            link_url: URL to navigate to
            
        Returns:
            Dict with navigation result
        """
        return self.open_website(link_url)
    
    # Legacy aliases for backward compatibility
    navigate = open_website
    get_elements = list_elements
    click_button = click_element
    fill_input = type_text
    submit_current_form = submit_form
    
    def _clean_content_for_display(self, markdown: str) -> str:
        """Clean markdown content to show proper page content like CLI browser"""
        lines = markdown.split('\n')
        clean_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Keep empty lines for formatting
            if not line_stripped:
                clean_lines.append('')
                continue
                
            # Skip JavaScript/technical patterns
            skip_patterns = [
                'window[', 'function(', 'console.log', 'var ', 'let ', 'const ',
                '():', '();', 'sl_tr_', '$.', 'jQuery', 'addEventListener',
                'createElement', 'getElementById', 'getElementsBy', 'tesla_cta',
                '"slides":', '"media":', '"componentList":', '"props":',
                '"desktopConfigOverwrite":', '"mobileConfigOverwrite":',
                '"tabletConfigOverwrite":', '"landscapeConfigOverwrite":',
                '"type":', '"name":', '"value":', '"gridRows":', '"gridCols":',
                'marginBlock', 'paddingBlock', 'marginInline', 'paddingInline',
                '"media_type":', '"roundedCorners":', '"alt_text":', '"source_type":',
                'while(paras[', '.template-landing-page', '.tds-footer'
            ]
            
            if any(skip in line_stripped for skip in skip_patterns):
                continue
                
            # Skip obvious JSON data lines
            if (line_stripped.startswith('"') and '":' in line_stripped) or \
               (line_stripped.count('"') > 2 and ':' in line_stripped):
                continue
                
            # Skip pure data lines with numbers and special chars
            if line_stripped.replace('"', '').replace(',', '').replace(':', '').replace(' ', '').isdigit():
                continue
                
            # Skip CSS-like syntax
            if line_stripped.endswith('{') and '.' in line_stripped:
                continue
                
            # Keep meaningful content: headers, text, links, etc.
            clean_lines.append(line)
        
        # Remove excessive empty lines
        result_lines = []
        empty_count = 0
        for line in clean_lines:
            if line.strip() == '':
                empty_count += 1
                if empty_count <= 2:  # Max 2 consecutive empty lines
                    result_lines.append(line)
            else:
                empty_count = 0
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _create_element_summary(self, buttons: List[dict], inputs: List[dict]) -> str:
        """Create a clean text summary of page elements"""
        summary_parts = []
        
        if buttons:
            summary_parts.append(f"Found {len(buttons)} clickable elements:")
            for btn in buttons:  # Show all buttons
                summary_parts.append(f"  {btn['number']}. {btn['text']} ({btn['type']})")
        
        if inputs:
            summary_parts.append(f"Found {len(inputs)} input fields:")
            for inp in inputs:  # Show all inputs
                placeholder = f" - {inp['placeholder']}" if inp['placeholder'] else ""
                summary_parts.append(f"  {inp['number']}. {inp['name']} ({inp['type']}){placeholder}")
        
        if not buttons and not inputs:
            summary_parts.append("No interactive elements found on this page.")
        
        return '\n'.join(summary_parts)
    
    def _extract_text_only_content(self, soup: BeautifulSoup) -> str:
        """Extract only meaningful text content from HTML, no markdown or technical elements"""
        if not soup:
            return ""
            
        # Remove script, style, and other technical elements
        for element in soup(['script', 'style', 'meta', 'link', 'noscript']):
            element.decompose()
        
        # Get all text content
        text_content = []
        
        # Process headings (h1-h6)
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = heading.get_text(strip=True)
            if text and len(text) > 2:
                level = int(heading.name[1])
                prefix = '#' * level + ' ' if level <= 3 else '## '
                text_content.append(f"{prefix}{text}")
                text_content.append("")  # Add spacing
        
        # Process paragraphs and main content
        for element in soup.find_all(['p', 'div', 'span', 'li', 'td', 'th']):
            text = element.get_text(strip=True)
            if text and len(text) > 3:
                # Skip if this text is already captured in a heading
                if not any(text in existing for existing in text_content):
                    # Clean up the text
                    text = ' '.join(text.split())  # Normalize whitespace
                    text_content.append(text)
        
        # Process lists specially
        for ul in soup.find_all(['ul', 'ol']):
            for li in ul.find_all('li'):
                text = li.get_text(strip=True)
                if text and len(text) > 2:
                    text_content.append(f"• {text}")
        
        # Join content and clean up
        full_text = '\n'.join(text_content)
        
        # Remove excessive empty lines
        lines = full_text.split('\n')
        clean_lines = []
        prev_empty = False
        
        for line in lines:
            line = line.strip()
            if line:
                clean_lines.append(line)
                prev_empty = False
            elif not prev_empty:
                clean_lines.append("")
                prev_empty = True
        
        return '\n'.join(clean_lines)