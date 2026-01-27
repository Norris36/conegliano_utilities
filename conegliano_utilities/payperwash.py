"""
PayPerWash Automation Module

Automates interaction with PayPerWash laundry booking system.
Uses requests with session handling to bypass 403 errors.

The PayPerWash system is an ASP.NET WebForms application that requires:
- Proper browser-like headers
- Session cookies
- ViewState and EventValidation tokens

Usage:
    from conegliano_utilities.payperwash import PayPerWash

    ppw = PayPerWash(facility_id="PPW0066")
    ppw.login(username="your_email", password="your_password")

    # Get available slots
    slots = ppw.get_available_slots()

    # Book a slot
    ppw.book_slot(day=1, time_slot=2)  # Tomorrow, 09:00-11:00
"""

import re
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta


@dataclass
class TimeSlot:
    """Represents a bookable time slot."""
    day_index: int
    slot_index: int
    resource_id: int
    date: str
    day_name: str
    start_time: str
    end_time: str
    is_available: bool
    slot_id: str
    title: str

    def __str__(self):
        status = "Available" if self.is_available else "Unavailable"
        return f"{self.day_name} {self.date} {self.start_time}-{self.end_time}: {status}"


class PayPerWashError(Exception):
    """Base exception for PayPerWash errors."""
    pass


class LoginError(PayPerWashError):
    """Raised when login fails."""
    pass


class BookingError(PayPerWashError):
    """Raised when booking fails."""
    pass


class PayPerWash:
    """
    PayPerWash laundry booking system automation.

    This class handles authentication and booking operations for PayPerWash
    laundry systems using the requests library with proper session handling.

    Attributes:
        facility_id (str): The facility identifier (e.g., "PPW0066")
        base_url (str): The base URL for the facility
        session (requests.Session): HTTP session with cookies
        is_logged_in (bool): Whether currently authenticated

    Example:
        >>> ppw = PayPerWash("PPW0066")
        >>> ppw.login("user@email.com", "password123")
        >>> slots = ppw.get_available_slots()
        >>> for slot in slots:
        ...     print(slot)
    """

    # Time slot mapping (slot index -> time range)
    TIME_SLOTS = {
        1: ("07:00", "09:00"),
        2: ("09:00", "11:00"),
        3: ("11:00", "13:00"),
        4: ("13:00", "15:00"),
        5: ("15:00", "17:00"),
        6: ("17:00", "19:00"),
        7: ("19:00", "21:00"),
        8: ("21:00", "23:00"),
    }

    # Danish day name mapping
    DAY_NAMES = {
        'Man': 'Monday',
        'Tir': 'Tuesday',
        'Ons': 'Wednesday',
        'Tor': 'Thursday',
        'Fre': 'Friday',
        'Lør': 'Saturday',
        'Søn': 'Sunday',
    }

    def __init__(self, facility_id: str = "PPW0066"):
        """
        Initialize PayPerWash client.

        Args:
            facility_id: The facility identifier (default: "PPW0066")
        """
        self.facility_id = facility_id
        self.base_url = f"https://web.payperwash.com/{facility_id}"

        # Create session with browser-like headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,da;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })

        self.is_logged_in = False
        self._viewstate = None
        self._viewstate_generator = None
        self._event_validation = None
        self._current_page = None

    def _extract_asp_tokens(self, html: str) -> Dict[str, str]:
        """
        Extract ASP.NET hidden field tokens from HTML.

        Args:
            html: The HTML content to parse

        Returns:
            Dictionary containing ViewState, EventValidation, etc.
        """
        soup = BeautifulSoup(html, 'html.parser')
        tokens = {}

        # Extract all hidden ASP.NET fields
        for field_name in ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION',
                           '__EVENTTARGET', '__EVENTARGUMENT']:
            field = soup.find('input', {'name': field_name})
            if field:
                tokens[field_name] = field.get('value', '')

        # Store for later use
        if '__VIEWSTATE' in tokens:
            self._viewstate = tokens['__VIEWSTATE']
        if '__VIEWSTATEGENERATOR' in tokens:
            self._viewstate_generator = tokens['__VIEWSTATEGENERATOR']
        if '__EVENTVALIDATION' in tokens:
            self._event_validation = tokens['__EVENTVALIDATION']

        return tokens

    def _get_page(self, page_name: str) -> requests.Response:
        """
        Fetch a page and extract ASP.NET tokens.

        Args:
            page_name: The page to fetch (e.g., "Default.aspx")

        Returns:
            The HTTP response
        """
        url = f"{self.base_url}/{page_name}"
        response = self.session.get(url)
        response.raise_for_status()
        self._extract_asp_tokens(response.text)
        self._current_page = response.text
        return response

    def _do_postback(self, page_name: str, event_target: str,
                     event_argument: str = "", extra_data: Dict[str, str] = None) -> requests.Response:
        """
        Perform an ASP.NET postback.

        Args:
            page_name: The target page
            event_target: The control triggering the postback
            event_argument: Arguments for the postback
            extra_data: Additional form fields

        Returns:
            The HTTP response
        """
        url = f"{self.base_url}/{page_name}"

        data = {
            '__EVENTTARGET': event_target,
            '__EVENTARGUMENT': event_argument,
            '__VIEWSTATE': self._viewstate or '',
            '__VIEWSTATEGENERATOR': self._viewstate_generator or '',
            '__EVENTVALIDATION': self._event_validation or '',
        }

        if extra_data:
            data.update(extra_data)

        # Update headers for POST
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://web.payperwash.com',
            'Referer': url,
        }

        response = self.session.post(url, data=data, headers=headers)
        response.raise_for_status()
        self._extract_asp_tokens(response.text)
        self._current_page = response.text
        return response

    def test_connection(self) -> Dict[str, Any]:
        """
        Test if we can connect to the PayPerWash server.

        Returns:
            Dictionary with connection test results
        """
        result = {
            'success': False,
            'status_code': None,
            'cookies': [],
            'is_login_page': False,
            'is_calendar_page': False,
            'error': None
        }

        try:
            response = self._get_page("Default.aspx")
            result['success'] = True
            result['status_code'] = response.status_code
            result['cookies'] = list(self.session.cookies.keys())

            # Check what page we got
            if 'txtBrugernavn' in response.text or 'txtPassword' in response.text:
                result['is_login_page'] = True
            if 'BookingCalendar' in response.text or 'Bestille' in response.text:
                result['is_calendar_page'] = True

        except requests.exceptions.RequestException as e:
            result['error'] = str(e)

        return result

    def get_login_page(self) -> Dict[str, Any]:
        """
        Fetch the login page and analyze its structure.

        Returns:
            Dictionary with login page analysis
        """
        response = self._get_page("Default.aspx")
        soup = BeautifulSoup(response.text, 'html.parser')

        result = {
            'status_code': response.status_code,
            'has_viewstate': self._viewstate is not None,
            'has_event_validation': self._event_validation is not None,
            'form_fields': [],
            'login_button': None,
        }

        # Find all input fields
        for inp in soup.find_all('input'):
            field_info = {
                'name': inp.get('name'),
                'id': inp.get('id'),
                'type': inp.get('type'),
            }
            if field_info['name'] and not field_info['name'].startswith('__'):
                result['form_fields'].append(field_info)

        # Find submit buttons
        for btn in soup.find_all(['input', 'button'], {'type': 'submit'}):
            if 'login' in str(btn).lower() or 'log' in btn.get('value', '').lower():
                result['login_button'] = {
                    'name': btn.get('name'),
                    'value': btn.get('value'),
                }

        return result

    def login(self, username: str, password: str) -> bool:
        """
        Log in to the PayPerWash system.

        Args:
            username: The login username (usually email)
            password: The login password

        Returns:
            True if login was successful

        Raises:
            LoginError: If login fails
        """
        # First, get the login page to obtain tokens
        response = self._get_page("Default.aspx")
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find username and password field names
        username_field = None
        password_field = None
        login_button = None

        for inp in soup.find_all('input'):
            name = inp.get('name', '')
            inp_type = inp.get('type', '')

            if 'brugernavn' in name.lower() or 'username' in name.lower() or 'email' in name.lower():
                username_field = name
            elif inp_type == 'password' or 'password' in name.lower() or 'kodeord' in name.lower():
                password_field = name
            elif inp_type == 'submit' and ('log' in name.lower() or 'login' in inp.get('value', '').lower()):
                login_button = name

        if not username_field or not password_field:
            # Try to find by common ASP.NET naming patterns
            for inp in soup.find_all('input'):
                name = inp.get('name', '')
                if 'txtBrugernavn' in name or 'txtUserName' in name:
                    username_field = name
                elif 'txtPassword' in name or 'txtKodeord' in name:
                    password_field = name
                elif 'btnLogin' in name or 'btLogin' in name:
                    login_button = name

        if not username_field or not password_field:
            raise LoginError(f"Could not find login form fields. Found inputs: {[inp.get('name') for inp in soup.find_all('input')]}")

        # Prepare login data
        login_data = {
            username_field: username,
            password_field: password,
        }

        if login_button:
            login_data[login_button] = 'Log ind'  # Danish for "Log in"

        # Submit login form
        response = self._do_postback("Default.aspx", "", "", login_data)

        # Check if login was successful
        # After successful login, we should be redirected to BookingCalendar or see the menu
        if 'LinkLogOut' in response.text or 'Log ud' in response.text:
            self.is_logged_in = True
            return True
        elif 'fejl' in response.text.lower() or 'error' in response.text.lower() or 'forkert' in response.text.lower():
            # Look for error message
            soup = BeautifulSoup(response.text, 'html.parser')
            error_span = soup.find('span', {'id': lambda x: x and 'message' in x.lower()})
            error_msg = error_span.text if error_span else "Unknown login error"
            raise LoginError(f"Login failed: {error_msg}")

        # Check if we're still on login page
        if 'txtBrugernavn' in response.text or 'txtPassword' in response.text:
            raise LoginError("Login failed: Still on login page after submission")

        self.is_logged_in = True
        return True

    def get_booking_calendar(self) -> requests.Response:
        """
        Navigate to the booking calendar page.

        Returns:
            The HTTP response containing the calendar
        """
        if not self.is_logged_in:
            raise PayPerWashError("Not logged in. Call login() first.")

        # Click on "Bestille" (Booking) link
        return self._do_postback("BookingCalendar.aspx", "ctl00$LinkBooking", "")

    def parse_calendar(self, html: str = None) -> List[TimeSlot]:
        """
        Parse the booking calendar and extract all time slots.

        Args:
            html: Optional HTML to parse (uses current page if not provided)

        Returns:
            List of TimeSlot objects
        """
        if html is None:
            html = self._current_page

        if html is None:
            raise PayPerWashError("No calendar page loaded. Call get_booking_calendar() first.")

        soup = BeautifulSoup(html, 'html.parser')
        slots = []

        # Extract day headers
        day_headers = {}
        for i in range(7):
            day_span = soup.find('span', {'id': f'lbCalendarDag{i}'})
            if day_span:
                text = day_span.get_text(separator=' ').strip()
                # Parse "Tir 27" format
                parts = text.split()
                if len(parts) >= 2:
                    day_name = parts[0]
                    day_date = parts[-1]
                    day_headers[i] = {'name': day_name, 'date': day_date}

        # Find all booking buttons
        # Pattern: input with id like "0,2,1,"
        slot_pattern = re.compile(r'^(\d+),(\d+),(\d+),$')

        for inp in soup.find_all('input', {'type': 'submit'}):
            inp_id = inp.get('id', '')
            match = slot_pattern.match(inp_id)

            if match:
                day_idx = int(match.group(1))
                slot_idx = int(match.group(2))
                resource_id = int(match.group(3))

                # Check availability
                is_disabled = inp.get('disabled') is not None or 'aspNetDisabled' in inp.get('class', [])
                bg_color = ''
                style = inp.get('style', '')
                if 'background-color' in style:
                    bg_match = re.search(r'background-color:\s*([#\w]+)', style)
                    if bg_match:
                        bg_color = bg_match.group(1)

                is_available = not is_disabled and bg_color.upper() in ['#00A000', '#0A0']

                # Get title (contains time info)
                title = inp.get('title', '')

                # Get time range
                start_time, end_time = self.TIME_SLOTS.get(slot_idx, ('??:??', '??:??'))

                # Get day info
                day_info = day_headers.get(day_idx, {'name': f'Day{day_idx}', 'date': '??'})

                slot = TimeSlot(
                    day_index=day_idx,
                    slot_index=slot_idx,
                    resource_id=resource_id,
                    date=day_info['date'],
                    day_name=day_info['name'],
                    start_time=start_time,
                    end_time=end_time,
                    is_available=is_available,
                    slot_id=inp_id,
                    title=title,
                )
                slots.append(slot)

        return slots

    def get_available_slots(self, html: str = None) -> List[TimeSlot]:
        """
        Get only the available (bookable) time slots.

        Args:
            html: Optional HTML to parse

        Returns:
            List of available TimeSlot objects
        """
        all_slots = self.parse_calendar(html)
        return [slot for slot in all_slots if slot.is_available]

    def book_slot(self, day: int = None, time_slot: int = None,
                  resource_id: int = 1, slot: TimeSlot = None) -> bool:
        """
        Book a specific time slot.

        Args:
            day: Day index (0=today, 1=tomorrow, etc.)
            time_slot: Time slot index (1=07:00-09:00, 2=09:00-11:00, etc.)
            resource_id: Resource/machine ID (usually 1)
            slot: Alternatively, pass a TimeSlot object directly

        Returns:
            True if booking was successful

        Raises:
            BookingError: If booking fails
        """
        if not self.is_logged_in:
            raise PayPerWashError("Not logged in. Call login() first.")

        if slot:
            day = slot.day_index
            time_slot = slot.slot_index
            resource_id = slot.resource_id

        if day is None or time_slot is None:
            raise BookingError("Must specify day and time_slot, or provide a TimeSlot object")

        slot_id = f"{day},{time_slot},{resource_id},"
        event_target = f"BookPass{slot_id}"

        # Perform the booking postback
        response = self._do_postback("BookingCalendar.aspx", event_target, slot_id)

        # Check for success/failure
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for error message
        message_panel = soup.find('div', {'id': 'PanelMessage'})
        if message_panel and 'display: none' not in message_panel.get('style', ''):
            message_text = soup.find('span', {'id': 'MessageText'})
            if message_text:
                msg = message_text.text.strip()
                if msg:
                    # Could be success or error - check message type
                    message_type = soup.find('input', {'id': 'MessageType'})
                    if message_type and message_type.get('value') == 'ERROR':
                        raise BookingError(f"Booking failed: {msg}")
                    else:
                        return True  # Success message

        # If no explicit error, assume success
        return True

    def get_balance(self) -> Optional[str]:
        """
        Get the current account balance.

        Returns:
            Balance string, or None if not available
        """
        if not self.is_logged_in:
            raise PayPerWashError("Not logged in. Call login() first.")

        # Navigate to balance page
        response = self._do_postback("Balance.aspx", "ctl00$LinkBalance", "")
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for balance display
        # Common patterns: "Saldo: XX,XX kr" or similar
        balance_text = None
        for span in soup.find_all('span'):
            text = span.text
            if 'kr' in text.lower() or 'saldo' in text.lower():
                balance_text = text.strip()
                break

        return balance_text

    def logout(self) -> bool:
        """
        Log out from the system.

        Returns:
            True if logout was successful
        """
        if not self.is_logged_in:
            return True

        self._do_postback("Default.aspx", "ctl00$LinkLogOut", "")
        self.is_logged_in = False
        return True

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure logout."""
        if self.is_logged_in:
            try:
                self.logout()
            except Exception:
                pass
        return False


def test_payperwash_connection(facility_id: str = "PPW0066") -> Dict[str, Any]:
    """
    Test connectivity to PayPerWash without logging in.

    Args:
        facility_id: The facility identifier

    Returns:
        Dictionary with test results
    """
    ppw = PayPerWash(facility_id)
    return ppw.test_connection()


def parse_calendar_html(html: str) -> List[TimeSlot]:
    """
    Parse calendar HTML without logging in.

    Useful for analyzing saved HTML or HTML provided by the user.

    Args:
        html: The HTML content to parse

    Returns:
        List of TimeSlot objects
    """
    ppw = PayPerWash()
    ppw._current_page = html
    return ppw.parse_calendar(html)


def get_available_slots_from_html(html: str) -> List[TimeSlot]:
    """
    Get available slots from calendar HTML.

    Args:
        html: The HTML content to parse

    Returns:
        List of available TimeSlot objects
    """
    all_slots = parse_calendar_html(html)
    return [slot for slot in all_slots if slot.is_available]
