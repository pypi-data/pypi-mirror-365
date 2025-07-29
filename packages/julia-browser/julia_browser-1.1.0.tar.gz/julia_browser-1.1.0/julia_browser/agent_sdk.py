"""
AI Agent SDK - Programming interface for AI agents to control Julia Browser
Provides all CLI browser interactions as callable functions for AI automation
"""

import json
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse

from .browser.engine import BrowserEngine
from .cli_interface import CLIBrowser


class AgentSDK:
    """
    AI Agent SDK for Julia Browser
    Provides programmatic access to all browser functionality for AI agents
    """
    
    def __init__(self, user_agent: str = None, timeout: int = 30):
        """
        Initialize Agent SDK
        
        Args:
            user_agent: Custom user agent string
            timeout: Default timeout for requests
        """
        self.engine = BrowserEngine(user_agent)
        self.cli_browser = CLIBrowser()
        self.current_url = None
        self.current_soup = None
        self.current_elements = {}
        self.default_timeout = timeout
        
    def navigate(self, url: str, execute_js: bool = True) -> Dict[str, Any]:
        """
        Navigate to a URL and return structured page data
        
        Args:
            url: URL to navigate to
            execute_js: Whether to execute JavaScript
            
        Returns:
            Dictionary with page content, elements, and metadata
        """
        try:
            # Fetch and render page
            success, content, soup = self.engine.fetch_page(url, self.default_timeout)
            
            if not success:
                return {
                    'success': False,
                    'error': content,
                    'url': url,
                    'timestamp': datetime.now().isoformat()
                }
            
            self.current_url = url
            self.current_soup = soup
            
            # Execute JavaScript if enabled
            if execute_js and soup:
                js_content = self.engine.extract_javascript(soup)
                if js_content:
                    js_output = self.engine.js_engine.execute_js(js_content, url)
                    if js_output.get('dom_updates'):
                        # Apply DOM updates to soup
                        self.engine.apply_dom_updates(soup, js_output['dom_updates'])
            
            # Render to markdown
            markdown_content = self.engine.render_page(soup)
            
            # Extract interactive elements
            elements = self._extract_elements(soup)
            self.current_elements = elements
            
            # Extract links
            links = self._extract_links(soup, url)
            
            return {
                'success': True,
                'url': url,
                'final_url': self.engine.current_url,
                'timestamp': datetime.now().isoformat(),
                'markdown': markdown_content,
                'raw_html': str(soup) if soup else '',
                'elements': elements,
                'links': links,
                'page_title': soup.title.string if soup and soup.title else '',
                'meta_description': self._get_meta_description(soup),
                'form_count': len(elements.get('forms', [])),
                'button_count': len(elements.get('buttons', [])),
                'input_count': len(elements.get('inputs', [])),
                'link_count': len(links)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Navigation error: {str(e)}",
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_elements(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all interactive elements on current page
        
        Returns:
            Dictionary with categorized elements (buttons, inputs, links, forms)
        """
        return self.current_elements
    
    def click_button(self, button_id: Union[int, str]) -> Dict[str, Any]:
        """
        Click a button by ID or number
        
        Args:
            button_id: Button identifier (number or element ID)
            
        Returns:
            Result of button click action
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No page loaded'}
        
        try:
            buttons = self.current_elements.get('buttons', [])
            
            if isinstance(button_id, int):
                if 0 <= button_id < len(buttons):
                    button_info = buttons[button_id]
                else:
                    return {'success': False, 'error': f'Button {button_id} not found'}
            else:
                button_info = next((b for b in buttons if b.get('id') == button_id), None)
                if not button_info:
                    return {'success': False, 'error': f'Button with ID {button_id} not found'}
            
            # Simulate button click
            result = self._handle_button_click(
                button_info, self.current_soup, self.current_url
            )
            
            # If navigation occurred, update current state
            if result.get('navigation_url'):
                nav_result = self.navigate(result['navigation_url'])
                result.update(nav_result)
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': f'Button click error: {str(e)}'}
    
    def fill_input(self, input_id: Union[int, str], value: str) -> Dict[str, Any]:
        """
        Fill an input field with text
        
        Args:
            input_id: Input field identifier (number or element ID)
            value: Text to enter
            
        Returns:
            Success status and input details
        """
        try:
            inputs = self.current_elements.get('inputs', [])
            
            if isinstance(input_id, int):
                if 0 <= input_id < len(inputs):
                    input_info = inputs[input_id]
                else:
                    return {'success': False, 'error': f'Input {input_id} not found'}
            else:
                input_info = next((i for i in inputs if i.get('id') == input_id or i.get('name') == input_id), None)
                if not input_info:
                    return {'success': False, 'error': f'Input with ID {input_id} not found'}
            
            # Store the typed value
            if not hasattr(self, 'form_data'):
                self.form_data = {}
            
            field_name = input_info.get('name') or input_info.get('id') or f'input_{input_id}'
            self.form_data[field_name] = value
            
            return {
                'success': True,
                'input_info': input_info,
                'value': value,
                'field_name': field_name
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Input fill error: {str(e)}'}
    
    def submit_form(self, form_id: Union[int, str] = None) -> Dict[str, Any]:
        """
        Submit a form on the current page
        
        Args:
            form_id: Form identifier (number or element ID), submits first form if None
            
        Returns:
            Result of form submission
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No page loaded'}
        
        try:
            forms = self.current_elements.get('forms', [])
            
            if not forms:
                return {'success': False, 'error': 'No forms found on page'}
            
            if form_id is None:
                form_info = forms[0]  # Submit first form
            elif isinstance(form_id, int):
                if 0 <= form_id < len(forms):
                    form_info = forms[form_id]
                else:
                    return {'success': False, 'error': f'Form {form_id} not found'}
            else:
                form_info = next((f for f in forms if f.get('id') == form_id), None)
                if not form_info:
                    return {'success': False, 'error': f'Form with ID {form_id} not found'}
            
            # Collect form data
            form_data = getattr(self, 'form_data', {})
            
            # Submit form
            result = self._submit_form_data(
                form_info, form_data, self.current_url
            )
            
            # Clear form data after submission
            self.form_data = {}
            
            # If navigation occurred, update current state
            if result.get('navigation_url'):
                nav_result = self.navigate(result['navigation_url'])
                result.update(nav_result)
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': f'Form submission error: {str(e)}'}
    
    def follow_link(self, link_id: Union[int, str]) -> Dict[str, Any]:
        """
        Follow a link by ID or number
        
        Args:
            link_id: Link identifier (number or text)
            
        Returns:
            Result of navigation
        """
        try:
            links = self.current_elements.get('links', [])
            
            if isinstance(link_id, int):
                if 0 <= link_id < len(links):
                    link_info = links[link_id]
                else:
                    return {'success': False, 'error': f'Link {link_id} not found'}
            else:
                # Search by text content
                link_info = next((l for l in links if link_id.lower() in l.get('text', '').lower()), None)
                if not link_info:
                    return {'success': False, 'error': f'Link containing "{link_id}" not found'}
            
            target_url = link_info.get('url')
            if not target_url:
                return {'success': False, 'error': 'Link has no URL'}
            
            # Navigate to link URL
            return self.navigate(target_url)
            
        except Exception as e:
            return {'success': False, 'error': f'Link follow error: {str(e)}'}
    
    def search_page(self, query: str) -> Dict[str, Any]:
        """
        Search for text content on the current page
        
        Args:
            query: Search query
            
        Returns:
            Search results with matches and context
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No page loaded'}
        
        try:
            # Get page text
            page_text = self.current_soup.get_text()
            
            # Find all matches
            matches = []
            for match in re.finditer(re.escape(query.lower()), page_text.lower()):
                start = max(0, match.start() - 50)
                end = min(len(page_text), match.end() + 50)
                context = page_text[start:end].strip()
                matches.append({
                    'position': match.start(),
                    'context': context,
                    'highlighted': context.replace(query, f"**{query}**")
                })
            
            return {
                'success': True,
                'query': query,
                'matches_found': len(matches),
                'matches': matches[:10]  # Return first 10 matches
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Search error: {str(e)}'}
    
    def get_page_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the current page
        
        Returns:
            Page metadata and statistics
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No page loaded'}
        
        try:
            return {
                'success': True,
                'url': self.current_url,
                'title': self.current_soup.title.string if self.current_soup.title else '',
                'meta_description': self._get_meta_description(self.current_soup),
                'word_count': len(self.current_soup.get_text().split()),
                'element_counts': {
                    'forms': len(self.current_elements.get('forms', [])),
                    'buttons': len(self.current_elements.get('buttons', [])),
                    'inputs': len(self.current_elements.get('inputs', [])),
                    'links': len(self.current_elements.get('links', []))
                },
                'has_javascript': bool(self.current_soup.find_all('script')),
                'has_forms': len(self.current_elements.get('forms', [])) > 0,
                'is_interactive': any([
                    self.current_elements.get('buttons'),
                    self.current_elements.get('inputs'),
                    self.current_elements.get('forms')
                ])
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Page info error: {str(e)}'}
    
    def execute_custom_action(self, action_type: str, **kwargs) -> Dict[str, Any]:
        """
        Execute custom browser actions
        
        Args:
            action_type: Type of action to execute
            **kwargs: Action parameters
            
        Returns:
            Action result
        """
        try:
            if action_type == 'scroll':
                return {'success': True, 'action': 'scroll', 'message': 'Scroll simulated'}
            
            elif action_type == 'wait':
                import time
                duration = kwargs.get('duration', 1)
                time.sleep(duration)
                return {'success': True, 'action': 'wait', 'duration': duration}
            
            elif action_type == 'screenshot':
                return {
                    'success': True, 
                    'action': 'screenshot', 
                    'message': 'Screenshot would be taken (text-based browser)'
                }
            
            elif action_type == 'refresh':
                if self.current_url:
                    return self.navigate(self.current_url)
                else:
                    return {'success': False, 'error': 'No page to refresh'}
            
            else:
                return {'success': False, 'error': f'Unknown action type: {action_type}'}
                
        except Exception as e:
            return {'success': False, 'error': f'Custom action error: {str(e)}'}
    
    def _extract_elements(self, soup) -> Dict[str, List[Dict[str, Any]]]:
        """Extract all interactive elements from the page"""
        if not soup:
            return {}
        
        elements = {
            'buttons': [],
            'inputs': [],
            'links': [],
            'forms': []
        }
        
        # Extract buttons
        for i, button in enumerate(soup.find_all(['button', 'input'])):
            if button.name == 'input' and button.get('type') not in ['submit', 'button', 'reset']:
                continue
            
            elements['buttons'].append({
                'id': button.get('id', f'button_{i}'),
                'text': button.get_text(strip=True) or button.get('value', ''),
                'type': button.get('type', 'button'),
                'class': button.get('class', []),
                'disabled': button.has_attr('disabled'),
                'form': button.get('form')
            })
        
        # Extract input fields
        for i, input_elem in enumerate(soup.find_all('input')):
            if input_elem.get('type') in ['submit', 'button', 'reset']:
                continue
            
            elements['inputs'].append({
                'id': input_elem.get('id', f'input_{i}'),
                'name': input_elem.get('name', ''),
                'type': input_elem.get('type', 'text'),
                'placeholder': input_elem.get('placeholder', ''),
                'value': input_elem.get('value', ''),
                'required': input_elem.has_attr('required'),
                'disabled': input_elem.has_attr('disabled')
            })
        
        # Extract textareas
        for i, textarea in enumerate(soup.find_all('textarea')):
            elements['inputs'].append({
                'id': textarea.get('id', f'textarea_{i}'),
                'name': textarea.get('name', ''),
                'type': 'textarea',
                'placeholder': textarea.get('placeholder', ''),
                'value': textarea.get_text(strip=True),
                'required': textarea.has_attr('required'),
                'disabled': textarea.has_attr('disabled')
            })
        
        # Extract forms
        for i, form in enumerate(soup.find_all('form')):
            elements['forms'].append({
                'id': form.get('id', f'form_{i}'),
                'action': form.get('action', ''),
                'method': form.get('method', 'GET').upper(),
                'name': form.get('name', ''),
                'target': form.get('target', '')
            })
        
        return elements
    
    def _extract_links(self, soup, base_url: str) -> List[Dict[str, Any]]:
        """Extract all links from the page"""
        if not soup:
            return []
        
        links = []
        for i, link in enumerate(soup.find_all('a', href=True)):
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                links.append({
                    'id': i,
                    'text': link.get_text(strip=True),
                    'url': full_url,
                    'title': link.get('title', ''),
                    'target': link.get('target', ''),
                    'rel': link.get('rel', [])
                })
        
        return links
    
    def _get_meta_description(self, soup) -> str:
        """Get meta description from page"""
        if not soup:
            return ''
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '')
        
        # Try property="description"
        meta_desc = soup.find('meta', attrs={'property': 'description'})
        if meta_desc:
            return meta_desc.get('content', '')
        
        return ''
    
    def _handle_button_click(self, button_info, soup, current_url):
        """Handle button click actions"""
        try:
            button_text = button_info.get('text', '').strip().lower()
            button_type = button_info.get('type', 'button').lower()
            
            # Check if it's a submit button
            if button_type in ['submit'] or 'submit' in button_text:
                # Find the associated form
                form_id = button_info.get('form')
                forms = self.current_elements.get('forms', [])
                
                if forms:
                    target_form = forms[0]  # Use first form if no specific form ID
                    if form_id:
                        target_form = next((f for f in forms if f.get('id') == form_id), forms[0])
                    
                    # Submit the form
                    form_data = getattr(self, 'form_data', {})
                    return self._submit_form_data(target_form, form_data, current_url)
            
            # Check if button has navigation URL
            onclick = button_info.get('onclick', '')
            if onclick and ('location' in onclick or 'href' in onclick):
                # Try to extract URL from onclick
                import re
                url_match = re.search(r'["\']([^"\']+)["\']', onclick)
                if url_match:
                    nav_url = url_match.group(1)
                    if nav_url.startswith('http'):
                        return {'success': True, 'navigation_url': nav_url}
            
            # Default button action
            return {
                'success': True,
                'action': 'button_clicked',
                'button_info': button_info,
                'message': f'Clicked button: {button_info.get("text", "unknown")}'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Button click error: {str(e)}'}
    
    def _submit_form_data(self, form_info, form_data, current_url):
        """Submit form data using HTTP request"""
        try:
            form_action = form_info.get('action', '')
            form_method = form_info.get('method', 'GET').upper()
            
            # Resolve form action URL
            if form_action:
                if form_action.startswith('http'):
                    submit_url = form_action
                else:
                    from urllib.parse import urljoin
                    submit_url = urljoin(current_url, form_action)
            else:
                submit_url = current_url
            
            # Submit the form
            if form_method == 'POST':
                response = self.engine.session.post(submit_url, data=form_data)
            else:
                response = self.engine.session.get(submit_url, params=form_data)
            
            response.raise_for_status()
            
            # Parse response
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Update current state
            self.current_url = response.url
            self.current_soup = soup
            self.current_elements = self._extract_elements(soup)
            
            # Render response
            markdown_content = self.engine.render_page(soup)
            
            return {
                'success': True,
                'form_action': form_action,
                'submit_url': submit_url,
                'method': form_method,
                'form_data': form_data,
                'navigation_url': response.url,
                'markdown': markdown_content,
                'response_text': response.text[:500] + '...' if len(response.text) > 500 else response.text
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Form submission error: {str(e)}'}