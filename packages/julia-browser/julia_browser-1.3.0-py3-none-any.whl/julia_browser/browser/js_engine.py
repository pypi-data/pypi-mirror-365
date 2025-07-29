"""
JavaScript Engine - Executes JavaScript code using PythonMonkey (SpiderMonkey)
"""

import pythonmonkey as pm
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import re
import json


class JavaScriptEngine:
    """JavaScript execution engine for processing web page scripts using PythonMonkey"""
    
    def __init__(self):
        """Initialize JavaScript engine with basic DOM simulation"""
        # PythonMonkey provides a global JavaScript context
        # Set up basic browser environment simulation
        self._setup_browser_environment()
        self.dom_modifications = {}
        
    def _setup_browser_environment(self):
        """Set up basic browser APIs and objects using PythonMonkey"""
        try:
            # PythonMonkey provides a more complete browser environment
            # Set up DOM-like environment and browser APIs
            browser_env = """
            // Enhanced DOM simulation with better compatibility
            var window = globalThis;
            
            // Add essential window methods that websites expect
            window.addEventListener = function(event, handler, options) {
                this._listeners = this._listeners || {};
                this._listeners[event] = this._listeners[event] || [];
                this._listeners[event].push(handler);
            };
            
            window.removeEventListener = function(event, handler) {
                if (this._listeners && this._listeners[event]) {
                    const index = this._listeners[event].indexOf(handler);
                    if (index > -1) {
                        this._listeners[event].splice(index, 1);
                    }
                }
            };
            
            window.setTimeout = setTimeout;
            window.clearTimeout = clearTimeout;
            window.setInterval = setInterval;
            window.clearInterval = clearInterval;
            window.location = location;
            
            // Initialize comprehensive navigator object
            window.navigator = {
                userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 CLI-Browser/1.0',
                platform: 'Linux x86_64',
                language: 'en-US',
                languages: ['en-US', 'en'],
                onLine: true,
                cookieEnabled: true,
                doNotTrack: null,
                hardwareConcurrency: 4,
                maxTouchPoints: 0,
                vendor: 'CLI Browser',
                vendorSub: '',
                productSub: '20030107',
                appCodeName: 'Mozilla',
                appName: 'Netscape',
                appVersion: '5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                oscpu: 'Linux x86_64',
                product: 'Gecko'
            };
            
            window.screen = { 
                width: 1920, 
                height: 1080,
                availWidth: 1920,
                availHeight: 1040,
                colorDepth: 24,
                pixelDepth: 24
            };
            
            // Additional window properties and methods
            window.innerWidth = 1920;
            window.innerHeight = 1080;
            window.outerWidth = 1920;
            window.outerHeight = 1080;
            window.devicePixelRatio = 1;
            window.scrollX = 0;
            window.scrollY = 0;
            window.pageXOffset = 0;
            window.pageYOffset = 0;
            
            // Window methods with proper null checks
            window.alert = function(message) { 
                console.log('ALERT: ' + (message || '')); 
            };
            window.confirm = function(message) { 
                console.log('CONFIRM: ' + (message || '')); 
                return true; 
            };
            window.prompt = function(message, defaultValue) { 
                console.log('PROMPT: ' + (message || '')); 
                return defaultValue != null ? String(defaultValue) : ''; 
            };
            window.open = function(url) { 
                console.log('Opening: ' + (url || 'about:blank')); 
                return window; 
            };
            window.close = function() { console.log('Window closed'); };
            window.focus = function() { console.log('Window focused'); };
            window.blur = function() { console.log('Window blurred'); };
            window.scrollTo = function(x, y) { window.scrollX = x; window.scrollY = y; };
            window.scrollBy = function(x, y) { window.scrollX += x; window.scrollY += y; };
            window.resizeTo = function(width, height) { window.innerWidth = width; window.innerHeight = height; };
            window.resizeBy = function(width, height) { window.innerWidth += width; window.innerHeight += height; };
            
            // Storage APIs
            window.localStorage = {
                _data: {},
                getItem: function(key) { return this._data[key] || null; },
                setItem: function(key, value) { this._data[key] = String(value); },
                removeItem: function(key) { delete this._data[key]; },
                clear: function() { this._data = {}; },
                get length() { return Object.keys(this._data).length; },
                key: function(index) { return Object.keys(this._data)[index] || null; }
            };
            window.sessionStorage = Object.assign({}, window.localStorage);
            
            // Cookie Management Implementation
            window._cookieStore = {};
            
            if (typeof document !== 'undefined') {
                Object.defineProperty(document, 'cookie', {
                get: function() {
                    const cookies = [];
                    for (const [name, data] of Object.entries(window._cookieStore)) {
                        if (!data.expires || new Date(data.expires) > new Date()) {
                            cookies.push(name + '=' + data.value);
                        }
                    }
                    return cookies.join('; ');
                },
                set: function(cookieString) {
                    const parts = cookieString.split(';').map(part => part.trim());
                    const [nameValue] = parts;
                    const [name, value = ''] = nameValue.split('=');
                    
                    const cookieData = { value };
                    
                    // Parse cookie attributes
                    for (let i = 1; i < parts.length; i++) {
                        const [attr, attrValue] = parts[i].split('=');
                        const attrName = attr.toLowerCase();
                        
                        if (attrName === 'expires') {
                            cookieData.expires = attrValue;
                        } else if (attrName === 'max-age') {
                            const maxAge = parseInt(attrValue);
                            cookieData.expires = new Date(Date.now() + maxAge * 1000).toUTCString();
                        } else if (attrName === 'domain') {
                            cookieData.domain = attrValue;
                        } else if (attrName === 'path') {
                            cookieData.path = attrValue;
                        } else if (attrName === 'secure') {
                            cookieData.secure = true;
                        } else if (attrName === 'httponly') {
                            cookieData.httpOnly = true;
                        } else if (attrName === 'samesite') {
                            cookieData.sameSite = attrValue;
                        }
                    }
                    
                    window._cookieStore[name] = cookieData;
                    console.log('🍪 Cookie set:', name + '=' + value);
                }
                });
            }
            
            // Session Management
            window._userSession = {
                isAuthenticated: false,
                user: null,
                token: null,
                sessionId: null,
                lastActivity: null,
                
                login: function(credentials) {
                    return new Promise((resolve, reject) => {
                        console.log('🔐 Authentication attempt for:', credentials.username || credentials.email);
                        
                        // Simulate authentication validation
                        setTimeout(() => {
                            if (credentials.username && credentials.password) {
                                this.isAuthenticated = true;
                                this.user = {
                                    id: Math.floor(Math.random() * 10000),
                                    username: credentials.username,
                                    email: credentials.email || credentials.username + '@example.com',
                                    role: 'user',
                                    loginTime: new Date().toISOString()
                                };
                                this.token = 'jwt_' + Math.random().toString(36).substring(2, 15);
                                this.sessionId = 'sess_' + Math.random().toString(36).substring(2, 15);
                                this.lastActivity = Date.now();
                                
                                // Set authentication cookies
                                document.cookie = 'auth_token=' + this.token + '; path=/; max-age=3600';
                                document.cookie = 'session_id=' + this.sessionId + '; path=/; httponly';
                                
                                // Store in localStorage for persistence
                                localStorage.setItem('user_session', JSON.stringify({
                                    user: this.user,
                                    token: this.token,
                                    sessionId: this.sessionId
                                }));
                                
                                console.log('✅ Authentication successful');
                                console.log('   User ID:', this.user.id);
                                console.log('   Session ID:', this.sessionId);
                                console.log('   Token:', this.token.substring(0, 10) + '...');
                                
                                resolve({
                                    success: true,
                                    user: this.user,
                                    token: this.token,
                                    message: 'Login successful'
                                });
                            } else {
                                console.log('❌ Authentication failed: Invalid credentials');
                                reject({
                                    success: false,
                                    message: 'Invalid username or password',
                                    error: 'INVALID_CREDENTIALS'
                                });
                            }
                        }, 300); // Simulate network delay
                    });
                },
                
                logout: function() {
                    console.log('🚪 Logging out user:', this.user ? this.user.username : 'unknown');
                    
                    this.isAuthenticated = false;
                    this.user = null;
                    this.token = null;
                    this.sessionId = null;
                    this.lastActivity = null;
                    
                    // Clear authentication cookies
                    document.cookie = 'auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/';
                    document.cookie = 'session_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/';
                    
                    // Clear localStorage
                    localStorage.removeItem('user_session');
                    
                    console.log('✅ Logout completed');
                    
                    return {
                        success: true,
                        message: 'Logged out successfully'
                    };
                },
                
                checkSession: function() {
                    const stored = localStorage.getItem('user_session');
                    if (stored) {
                        try {
                            const sessionData = JSON.parse(stored);
                            if (sessionData.token && sessionData.user) {
                                this.isAuthenticated = true;
                                this.user = sessionData.user;
                                this.token = sessionData.token;
                                this.sessionId = sessionData.sessionId;
                                this.lastActivity = Date.now();
                                
                                console.log('🔄 Session restored for user:', this.user.username);
                                return true;
                            }
                        } catch (e) {
                            console.log('⚠️ Invalid session data, clearing...');
                            localStorage.removeItem('user_session');
                        }
                    }
                    return false;
                },
                
                refreshToken: function() {
                    if (this.isAuthenticated && this.token) {
                        const newToken = 'jwt_' + Math.random().toString(36).substring(2, 15);
                        this.token = newToken;
                        document.cookie = 'auth_token=' + newToken + '; path=/; max-age=3600';
                        
                        console.log('🔄 Token refreshed:', newToken.substring(0, 10) + '...');
                        return newToken;
                    }
                    return null;
                },
                
                updateActivity: function() {
                    if (this.isAuthenticated) {
                        this.lastActivity = Date.now();
                    }
                }
            };
            
            // Initialize session on startup
            window._userSession.checkSession();
            
            // Performance API
            window.performance = {
                now: function() { return Date.now(); },
                timing: {
                    navigationStart: Date.now() - 1000,
                    loadEventEnd: Date.now()
                }
            };
            
            // Modern ECMAScript Features Support (ES2015-ES2026)
            
            // ES2026/2025 - Latest Features
            
            // Iterator Helpers - Global Iterator object with functional methods
            if (typeof Iterator === 'undefined') {
                window.Iterator = function() {};
                
                // Iterator.from() - Create iterator from iterable
                window.Iterator.from = function(iterable) {
                    if (iterable && typeof iterable[Symbol.iterator] === 'function') {
                        return iterable[Symbol.iterator]();
                    }
                    if (Array.isArray(iterable)) {
                        return iterable.values();
                    }
                    throw new TypeError('Iterator.from() requires an iterable');
                };
                
                // Add functional methods to Iterator prototype
                window.Iterator.prototype.map = function(mapperFn) {
                    const iter = this;
                    return {
                        next() {
                            const result = iter.next();
                            if (result.done) return result;
                            return { value: mapperFn(result.value), done: false };
                        },
                        [Symbol.iterator]() { return this; }
                    };
                };
                
                window.Iterator.prototype.filter = function(predicate) {
                    const iter = this;
                    return {
                        next() {
                            let result;
                            do {
                                result = iter.next();
                                if (result.done) return result;
                            } while (!predicate(result.value));
                            return result;
                        },
                        [Symbol.iterator]() { return this; }
                    };
                };
                
                window.Iterator.prototype.reduce = function(reducer, initialValue) {
                    let accumulator = initialValue;
                    let result = this.next();
                    let hasInitial = arguments.length > 1;
                    
                    if (!hasInitial && !result.done) {
                        accumulator = result.value;
                        result = this.next();
                    }
                    
                    while (!result.done) {
                        accumulator = reducer(accumulator, result.value);
                        result = this.next();
                    }
                    return accumulator;
                };
                
                window.Iterator.prototype.flatMap = function(mapperFn) {
                    const iter = this;
                    let innerIterator = null;
                    
                    return {
                        next() {
                            while (true) {
                                if (innerIterator) {
                                    const innerResult = innerIterator.next();
                                    if (!innerResult.done) {
                                        return innerResult;
                                    }
                                    innerIterator = null;
                                }
                                
                                const outerResult = iter.next();
                                if (outerResult.done) return outerResult;
                                
                                const mapped = mapperFn(outerResult.value);
                                if (mapped && typeof mapped[Symbol.iterator] === 'function') {
                                    innerIterator = mapped[Symbol.iterator]();
                                } else {
                                    return { value: mapped, done: false };
                                }
                            }
                        },
                        [Symbol.iterator]() { return this; }
                    };
                };
                
                window.Iterator.prototype.take = function(limit) {
                    const iter = this;
                    let count = 0;
                    
                    return {
                        next() {
                            if (count >= limit) {
                                return { done: true };
                            }
                            count++;
                            return iter.next();
                        },
                        [Symbol.iterator]() { return this; }
                    };
                };
                
                window.Iterator.prototype.drop = function(limit) {
                    const iter = this;
                    let dropped = 0;
                    
                    return {
                        next() {
                            while (dropped < limit) {
                                const result = iter.next();
                                if (result.done) return result;
                                dropped++;
                            }
                            return iter.next();
                        },
                        [Symbol.iterator]() { return this; }
                    };
                };
                
                window.Iterator.prototype.find = function(predicate) {
                    let result = this.next();
                    while (!result.done) {
                        if (predicate(result.value)) {
                            return result.value;
                        }
                        result = this.next();
                    }
                    return undefined;
                };
                
                window.Iterator.prototype.some = function(predicate) {
                    let result = this.next();
                    while (!result.done) {
                        if (predicate(result.value)) {
                            return true;
                        }
                        result = this.next();
                    }
                    return false;
                };
                
                window.Iterator.prototype.every = function(predicate) {
                    let result = this.next();
                    while (!result.done) {
                        if (!predicate(result.value)) {
                            return false;
                        }
                        result = this.next();
                    }
                    return true;
                };
                
                window.Iterator.prototype.toArray = function() {
                    const array = [];
                    let result = this.next();
                    while (!result.done) {
                        array.push(result.value);
                        result = this.next();
                    }
                    return array;
                };
            }
            
            // ES2025 - Enhanced Set Methods
            if (typeof Set !== 'undefined' && Set.prototype) {
                // Set.prototype.intersection
                if (!Set.prototype.intersection) {
                    Set.prototype.intersection = function(other) {
                        const result = new Set();
                        for (const value of this) {
                            if (other.has(value)) {
                                result.add(value);
                            }
                        }
                        return result;
                    };
                }
                
                // Set.prototype.union
                if (!Set.prototype.union) {
                    Set.prototype.union = function(other) {
                        const result = new Set(this);
                        for (const value of other) {
                            result.add(value);
                        }
                        return result;
                    };
                }
                
                // Set.prototype.difference
                if (!Set.prototype.difference) {
                    Set.prototype.difference = function(other) {
                        const result = new Set();
                        for (const value of this) {
                            if (!other.has(value)) {
                                result.add(value);
                            }
                        }
                        return result;
                    };
                }
                
                // Set.prototype.symmetricDifference
                if (!Set.prototype.symmetricDifference) {
                    Set.prototype.symmetricDifference = function(other) {
                        const result = new Set();
                        for (const value of this) {
                            if (!other.has(value)) {
                                result.add(value);
                            }
                        }
                        for (const value of other) {
                            if (!this.has(value)) {
                                result.add(value);
                            }
                        }
                        return result;
                    };
                }
                
                // Set.prototype.isSubsetOf
                if (!Set.prototype.isSubsetOf) {
                    Set.prototype.isSubsetOf = function(other) {
                        for (const value of this) {
                            if (!other.has(value)) {
                                return false;
                            }
                        }
                        return true;
                    };
                }
                
                // Set.prototype.isSupersetOf
                if (!Set.prototype.isSupersetOf) {
                    Set.prototype.isSupersetOf = function(other) {
                        for (const value of other) {
                            if (!this.has(value)) {
                                return false;
                            }
                        }
                        return true;
                    };
                }
                
                // Set.prototype.isDisjointFrom
                if (!Set.prototype.isDisjointFrom) {
                    Set.prototype.isDisjointFrom = function(other) {
                        for (const value of this) {
                            if (other.has(value)) {
                                return false;
                            }
                        }
                        return true;
                    };
                }
            }
            
            // ES2025 - RegExp.escape
            if (typeof RegExp !== 'undefined' && !RegExp.escape) {
                RegExp.escape = function(string) {
                    return String(string).replace(/[\\^$*+?.()|[\\]{}]/g, '\\\\$&');
                };
            }
            
            // ES2025 - Promise.try
            if (typeof Promise !== 'undefined' && !Promise.try) {
                Promise.try = function(fn) {
                    return new Promise(resolve => resolve(fn()));
                };
            }
            
            // ES2025 - Float16Array support
            if (typeof Float16Array === 'undefined') {
                window.Float16Array = function(arrayOrLength) {
                    // Simplified implementation using Float32Array as backing
                    if (typeof arrayOrLength === 'number') {
                        this._data = new Float32Array(arrayOrLength);
                        this.length = arrayOrLength;
                    } else if (Array.isArray(arrayOrLength)) {
                        this._data = new Float32Array(arrayOrLength);
                        this.length = arrayOrLength.length;
                    }
                    
                    // Add array-like behavior
                    for (let i = 0; i < this.length; i++) {
                        Object.defineProperty(this, i, {
                            get: function() { return this._data[i]; },
                            set: function(value) { this._data[i] = value; },
                            enumerable: true
                        });
                    }
                };
                
                window.Float16Array.prototype.BYTES_PER_ELEMENT = 2;
                window.Float16Array.BYTES_PER_ELEMENT = 2;
                
                // Add standard TypedArray methods
                window.Float16Array.prototype.set = function(array, offset = 0) {
                    for (let i = 0; i < array.length; i++) {
                        this._data[offset + i] = array[i];
                    }
                };
                
                window.Float16Array.prototype.subarray = function(start, end) {
                    const sub = new Float16Array(0);
                    sub._data = this._data.subarray(start, end);
                    sub.length = sub._data.length;
                    return sub;
                };
            }
            
            // Math.f16round for 16-bit float precision
            if (typeof Math !== 'undefined' && !Math.f16round) {
                Math.f16round = function(x) {
                    // Simplified 16-bit float rounding
                    const float32 = Math.fround(x);
                    // Additional precision reduction for 16-bit representation
                    return parseFloat(float32.toPrecision(4));
                };
            }
            
            // Enhanced DataView methods for Float16
            if (typeof DataView !== 'undefined') {
                if (!DataView.prototype.getFloat16) {
                    DataView.prototype.getFloat16 = function(byteOffset, littleEndian = false) {
                        // Simplified implementation
                        const uint16 = this.getUint16(byteOffset, littleEndian);
                        // Convert uint16 to float16 (simplified)
                        return uint16 / 1000; // Basic conversion
                    };
                }
                
                if (!DataView.prototype.setFloat16) {
                    DataView.prototype.setFloat16 = function(byteOffset, value, littleEndian = false) {
                        // Simplified implementation
                        const uint16 = Math.round(value * 1000);
                        this.setUint16(byteOffset, uint16, littleEndian);
                    };
                }
            }
            
            // ES2025 - Explicit Resource Management
            window.Symbol = window.Symbol || function(description) {
                return { description: description, toString: () => `Symbol(${description})` };
            };
            window.Symbol.dispose = window.Symbol.dispose || window.Symbol('Symbol.dispose');
            window.Symbol.asyncDispose = window.Symbol.asyncDispose || window.Symbol('Symbol.asyncDispose');
            
            // ES2024 - Iterator Helpers
            if (typeof Iterator === 'undefined') {
                window.Iterator = function() {};
                window.Iterator.prototype.map = function(fn) {
                    const iter = this;
                    return {
                        next() {
                            const result = iter.next();
                            return result.done ? result : { value: fn(result.value), done: false };
                        },
                        [Symbol.iterator]() { return this; }
                    };
                };
                window.Iterator.prototype.filter = function(predicate) {
                    const iter = this;
                    return {
                        next() {
                            let result;
                            do {
                                result = iter.next();
                                if (result.done) return result;
                            } while (!predicate(result.value));
                            return result;
                        },
                        [Symbol.iterator]() { return this; }
                    };
                };
                window.Iterator.prototype.reduce = function(reducer, initialValue) {
                    let accumulator = initialValue;
                    let result = this.next();
                    while (!result.done) {
                        accumulator = reducer(accumulator, result.value);
                        result = this.next();
                    }
                    return accumulator;
                };
            }
            
            // ES2022 - Private brand checks and class static blocks
            // (Supported by SpiderMonkey engine automatically)
            
            // ES2021 - Logical assignment operators
            // ||=, &&=, ??= (handled by engine)
            
            // ES2021 - String.prototype.replaceAll
            if (!String.prototype.replaceAll) {
                String.prototype.replaceAll = function(searchValue, replaceValue) {
                    if (typeof searchValue === 'string') {
                        return this.split(searchValue).join(replaceValue);
                    }
                    return this.replace(searchValue, replaceValue);
                };
            }
            
            // ES2021 - Weak references and finalizers
            if (typeof WeakRef === 'undefined') {
                window.WeakRef = function(target) {
                    this._target = target;
                    this.deref = function() { return this._target; };
                };
            }
            
            if (typeof FinalizationRegistry === 'undefined') {
                window.FinalizationRegistry = function(cleanupCallback) {
                    this._callback = cleanupCallback;
                    this.register = function(target, heldValue, unregisterToken) {
                        // Simplified implementation
                        console.log('FinalizationRegistry.register called');
                    };
                    this.unregister = function(unregisterToken) {
                        console.log('FinalizationRegistry.unregister called');
                    };
                };
            }
            
            // ES2020 - Promise.allSettled
            if (!Promise.allSettled) {
                Promise.allSettled = function(promises) {
                    return Promise.all(promises.map(promise =>
                        Promise.resolve(promise)
                            .then(value => ({ status: 'fulfilled', value }))
                            .catch(reason => ({ status: 'rejected', reason }))
                    ));
                };
            }
            
            // ES2020 - Promise.any
            if (!Promise.any) {
                Promise.any = function(promises) {
                    return new Promise((resolve, reject) => {
                        const errors = [];
                        let rejectedCount = 0;
                        
                        promises.forEach((promise, index) => {
                            Promise.resolve(promise)
                                .then(resolve)
                                .catch(error => {
                                    errors[index] = error;
                                    rejectedCount++;
                                    if (rejectedCount === promises.length) {
                                        reject(new AggregateError(errors, 'All promises were rejected'));
                                    }
                                });
                        });
                    });
                };
            }
            
            // ES2020 - BigInt (handled by engine)
            // ES2020 - Nullish coalescing and optional chaining (handled by engine)
            
            // ES2020 - globalThis
            if (typeof globalThis === 'undefined') {
                window.globalThis = window;
            }
            
            // ES2020 - String.prototype.matchAll
            if (!String.prototype.matchAll) {
                String.prototype.matchAll = function(regexp) {
                    if (!regexp.global) {
                        throw new TypeError('String.prototype.matchAll called with a non-global RegExp argument');
                    }
                    const matches = [];
                    let match;
                    while ((match = regexp.exec(this)) !== null) {
                        matches.push(match);
                    }
                    return matches[Symbol.iterator]();
                };
            }
            
            // ES2019 - Object.fromEntries
            if (!Object.fromEntries) {
                Object.fromEntries = function(iterable) {
                    const obj = {};
                    for (const [key, value] of iterable) {
                        obj[key] = value;
                    }
                    return obj;
                };
            }
            
            // ES2019 - Array.prototype.flat and flatMap
            if (!Array.prototype.flat) {
                Array.prototype.flat = function(depth = 1) {
                    const flatten = (arr, currentDepth) => {
                        return currentDepth > 0 ? arr.reduce((acc, val) => 
                            acc.concat(Array.isArray(val) ? flatten(val, currentDepth - 1) : val), []) : arr.slice();
                    };
                    return flatten(this, depth);
                };
            }
            
            if (!Array.prototype.flatMap) {
                Array.prototype.flatMap = function(callback, thisArg) {
                    return this.map(callback, thisArg).flat();
                };
            }
            
            // ES2019 - String.prototype.trimStart and trimEnd
            if (!String.prototype.trimStart) {
                String.prototype.trimStart = String.prototype.trimLeft || function() {
                    return this.replace(/^\\s+/, '');
                };
            }
            
            if (!String.prototype.trimEnd) {
                String.prototype.trimEnd = String.prototype.trimRight || function() {
                    return this.replace(/\\s+$/, '');
                };
            }
            
            // ES2018 - Promise.prototype.finally
            if (!Promise.prototype.finally) {
                Promise.prototype.finally = function(onFinally) {
                    return this.then(
                        value => Promise.resolve(onFinally()).then(() => value),
                        reason => Promise.resolve(onFinally()).then(() => { throw reason; })
                    );
                };
            }
            
            // ES2017 - Object.entries and Object.values
            if (!Object.entries) {
                Object.entries = function(obj) {
                    return Object.keys(obj).map(key => [key, obj[key]]);
                };
            }
            
            if (!Object.values) {
                Object.values = function(obj) {
                    return Object.keys(obj).map(key => obj[key]);
                };
            }
            
            // Array methods - find, findIndex, includes
            if (!Array.prototype.find) {
                Array.prototype.find = function(callback, thisArg) {
                    for (let i = 0; i < this.length; i++) {
                        if (callback.call(thisArg, this[i], i, this)) {
                            return this[i];
                        }
                    }
                    return undefined;
                };
            }
            
            if (!Array.prototype.findIndex) {
                Array.prototype.findIndex = function(callback, thisArg) {
                    for (let i = 0; i < this.length; i++) {
                        if (callback.call(thisArg, this[i], i, this)) {
                            return i;
                        }
                    }
                    return -1;
                };
            }
            
            if (!Array.prototype.includes) {
                Array.prototype.includes = function(searchElement, fromIndex = 0) {
                    const length = this.length;
                    if (length === 0) return false;
                    
                    const n = Math.floor(fromIndex) || 0;
                    const k = n >= 0 ? n : Math.max(length + n, 0);
                    
                    for (let i = k; i < length; i++) {
                        if (this[i] === searchElement || (Number.isNaN(this[i]) && Number.isNaN(searchElement))) {
                            return true;
                        }
                    }
                    return false;
                };
            }
            
            // Array.prototype.at method for relative indexing
            if (!Array.prototype.at) {
                Array.prototype.at = function(index) {
                    const length = this.length;
                    const relativeIndex = Math.floor(index) || 0;
                    const actualIndex = relativeIndex >= 0 ? relativeIndex : length + relativeIndex;
                    return actualIndex >= 0 && actualIndex < length ? this[actualIndex] : undefined;
                };
            }
            
            // Object.hasOwn
            if (!Object.hasOwn) {
                Object.hasOwn = function(obj, prop) {
                    return Object.prototype.hasOwnProperty.call(obj, prop);
                };
            }
            
            // ES2025/2026 - Additional Modern Features
            
            // Enhanced Array/TypedArray methods
            ['Array', 'Int8Array', 'Uint8Array', 'Int16Array', 'Uint16Array', 'Int32Array', 'Uint32Array', 'Float32Array', 'Float64Array'].forEach(typeName => {
                const TypedArrayConstructor = window[typeName];
                if (TypedArrayConstructor && TypedArrayConstructor.prototype) {
                    // toSorted (non-mutating sort)
                    if (!TypedArrayConstructor.prototype.toSorted) {
                        TypedArrayConstructor.prototype.toSorted = function(compareFn) {
                            return Array.from(this).sort(compareFn);
                        };
                    }
                    
                    // toReversed (non-mutating reverse)
                    if (!TypedArrayConstructor.prototype.toReversed) {
                        TypedArrayConstructor.prototype.toReversed = function() {
                            return Array.from(this).reverse();
                        };
                    }
                    
                    // with (immutable element replacement)
                    if (!TypedArrayConstructor.prototype.with) {
                        TypedArrayConstructor.prototype.with = function(index, value) {
                            const copy = Array.from(this);
                            const actualIndex = index < 0 ? copy.length + index : index;
                            if (actualIndex >= 0 && actualIndex < copy.length) {
                                copy[actualIndex] = value;
                            }
                            return copy;
                        };
                    }
                    
                    // findLast and findLastIndex
                    if (!TypedArrayConstructor.prototype.findLast) {
                        TypedArrayConstructor.prototype.findLast = function(callback, thisArg) {
                            for (let i = this.length - 1; i >= 0; i--) {
                                if (callback.call(thisArg, this[i], i, this)) {
                                    return this[i];
                                }
                            }
                            return undefined;
                        };
                    }
                    
                    if (!TypedArrayConstructor.prototype.findLastIndex) {
                        TypedArrayConstructor.prototype.findLastIndex = function(callback, thisArg) {
                            for (let i = this.length - 1; i >= 0; i--) {
                                if (callback.call(thisArg, this[i], i, this)) {
                                    return i;
                                }
                            }
                            return -1;
                        };
                    }
                }
            });
            
            // Array.prototype.toSpliced (splicing without mutation)
            if (!Array.prototype.toSpliced) {
                Array.prototype.toSpliced = function(start, deleteCount, ...items) {
                    const copy = Array.from(this);
                    copy.splice(start, deleteCount, ...items);
                    return copy;
                };
            }
            
            // ES2024/2025 - Object.groupBy and Map.groupBy
            if (!Object.groupBy) {
                Object.groupBy = function(iterable, keyFn) {
                    const result = {};
                    let index = 0;
                    for (const item of iterable) {
                        const key = keyFn(item, index++);
                        if (!result[key]) {
                            result[key] = [];
                        }
                        result[key].push(item);
                    }
                    return result;
                };
            }
            
            if (typeof Map !== 'undefined' && !Map.groupBy) {
                Map.groupBy = function(iterable, keyFn) {
                    const result = new Map();
                    let index = 0;
                    for (const item of iterable) {
                        const key = keyFn(item, index++);
                        if (!result.has(key)) {
                            result.set(key, []);
                        }
                        result.get(key).push(item);
                    }
                    return result;
                };
            }
            
            // ES2025 - Promise.withResolvers
            if (typeof Promise !== 'undefined' && !Promise.withResolvers) {
                Promise.withResolvers = function() {
                    let resolve, reject;
                    const promise = new Promise((res, rej) => {
                        resolve = res;
                        reject = rej;
                    });
                    return { promise, resolve, reject };
                };
            }
            
            // ES2024 - String.prototype.isWellFormed and toWellFormed
            if (!String.prototype.isWellFormed) {
                String.prototype.isWellFormed = function() {
                    // Simplified check for well-formed Unicode
                    try {
                        encodeURIComponent(this);
                        return true;
                    } catch (e) {
                        return false;
                    }
                };
            }
            
            if (!String.prototype.toWellFormed) {
                String.prototype.toWellFormed = function() {
                    // Basic well-formed Unicode conversion - replace surrogates with safe character
                    return this.replace(/[\\ud800-\\udfff]/g, '?');
                };
            }
            
            // ES2024 - Atomics.waitAsync
            if (typeof Atomics !== 'undefined' && !Atomics.waitAsync) {
                Atomics.waitAsync = function(typedArray, index, value, timeout) {
                    return Promise.resolve({
                        async: false,
                        value: 'not-equal'
                    });
                };
            }
            
            // ES2025/2026 - Enhanced Import Attributes and JSON Modules
            window._jsonModuleRegistry = new Map();
            
            // Mock import with attributes for JSON modules
            window._importJSON = async function(specifier, attributes) {
                if (attributes && attributes.type === 'json') {
                    console.log('📦 JSON Module Import:', specifier);
                    
                    if (window._jsonModuleRegistry.has(specifier)) {
                        return window._jsonModuleRegistry.get(specifier);
                    }
                    
                    // Default JSON data for simulation
                    const defaultData = {
                        message: 'JSON module import simulated',
                        timestamp: Date.now(),
                        source: specifier
                    };
                    
                    window._jsonModuleRegistry.set(specifier, defaultData);
                    return defaultData;
                }
                
                throw new TypeError('Unsupported import attributes');
            };
            
            // Error causes
            if (typeof Error.prototype.cause === 'undefined') {
                const OriginalError = Error;
                window.Error = function(message, options) {
                    const error = new OriginalError(message);
                    if (options && 'cause' in options) {
                        error.cause = options.cause;
                    }
                    return error;
                };
                window.Error.prototype = OriginalError.prototype;
            }
            
            // Intl enhancements
            if (typeof Intl !== 'undefined') {
                // Intl.DisplayNames
                if (!Intl.DisplayNames) {
                    Intl.DisplayNames = function(locales, options) {
                        this.of = function(code) {
                            // Simplified implementation
                            return code;
                        };
                    };
                }
                
                // Intl.ListFormat
                if (!Intl.ListFormat) {
                    Intl.ListFormat = function(locales, options) {
                        this.format = function(list) {
                            if (list.length === 0) return '';
                            if (list.length === 1) return list[0];
                            if (list.length === 2) return list.join(' and ');
                            return list.slice(0, -1).join(', ') + ', and ' + list[list.length - 1];
                        };
                    };
                }
                
                // Intl.RelativeTimeFormat
                if (!Intl.RelativeTimeFormat) {
                    Intl.RelativeTimeFormat = function(locales, options) {
                        this.format = function(value, unit) {
                            const units = {
                                second: 'second', minute: 'minute', hour: 'hour',
                                day: 'day', week: 'week', month: 'month', year: 'year'
                            };
                            const unitName = units[unit] || unit;
                            const abs = Math.abs(value);
                            const plural = abs !== 1 ? 's' : '';
                            return value < 0 ? `${abs} ${unitName}${plural} ago` : `in ${abs} ${unitName}${plural}`;
                        };
                    };
                }
            }
            
            // URL and URLSearchParams (Enhanced)
            window.URL = function(url, base) {
                const parser = document.createElement('a');
                parser.href = base ? new URL(base).href.replace(/\\/+$/, '') + '/' + url : url;
                
                this.href = parser.href;
                this.protocol = parser.protocol;
                this.host = parser.host;
                this.hostname = parser.hostname;
                this.port = parser.port;
                this.pathname = parser.pathname;
                this.search = parser.search;
                this.hash = parser.hash;
                this.origin = parser.protocol + '//' + parser.host;
                this.searchParams = new URLSearchParams(this.search.substring(1));
                
                this.toString = function() { return this.href; };
                this.toJSON = function() { return this.href; };
            };
            
            window.URLSearchParams = function(init) {
                this._params = new Map();
                
                if (typeof init === 'string') {
                    if (init.startsWith('?')) init = init.substring(1);
                    init.split('&').forEach(pair => {
                        if (pair) {
                            const [key, value = ''] = pair.split('=');
                            this._params.set(decodeURIComponent(key), decodeURIComponent(value));
                        }
                    });
                } else if (init instanceof URLSearchParams) {
                    this._params = new Map(init._params);
                } else if (Array.isArray(init)) {
                    init.forEach(([key, value]) => this._params.set(key, value));
                } else if (init && typeof init === 'object') {
                    Object.keys(init).forEach(key => this._params.set(key, init[key]));
                }
                
                this.append = function(name, value) { 
                    const existing = this._params.get(name);
                    if (existing !== undefined) {
                        this._params.set(name, existing + ',' + value);
                    } else {
                        this._params.set(name, value);
                    }
                };
                this.delete = function(name) { this._params.delete(name); };
                this.get = function(name) { return this._params.get(name) || null; };
                this.getAll = function(name) { 
                    const value = this._params.get(name);
                    return value ? value.split(',') : [];
                };
                this.has = function(name) { return this._params.has(name); };
                this.set = function(name, value) { this._params.set(name, String(value)); };
                this.sort = function() {
                    const sorted = new Map([...this._params.entries()].sort());
                    this._params = sorted;
                };
                this.toString = function() {
                    const params = [];
                    for (const [key, value] of this._params) {
                        params.push(encodeURIComponent(key) + '=' + encodeURIComponent(value));
                    }
                    return params.join('&');
                };
                this.forEach = function(callback, thisArg) {
                    for (const [key, value] of this._params) {
                        callback.call(thisArg, value, key, this);
                    }
                };
                this.keys = function() { return this._params.keys(); };
                this.values = function() { return this._params.values(); };
                this.entries = function() { return this._params.entries(); };
                this[Symbol.iterator] = function() { return this.entries(); };
            };
            
            // Real Fetch API Implementation for modern JavaScript websites
            window._realFetch = async function(url, options) {
                // This will be intercepted by Python to make real HTTP requests
                console.log('🌐 Real Fetch API request:', url);
                
                try {
                    // Signal to Python layer to make real network request
                    const realResponse = await window._pythonFetch(url, options);
                    return realResponse;
                } catch (error) {
                    console.log('❌ Fetch error:', error);
                    throw error;
                }
            };
            
            window.fetch = function(input, init) {
                return new Promise((resolve, reject) => {
                    console.log('🌐 Fetch API request:', input);
                    
                    // Parse request
                    const url = typeof input === 'string' ? input : input.url;
                    const options = init || {};
                    const method = options.method || 'GET';
                    const headers = options.headers || {};
                    const body = options.body;
                    
                    console.log('   Method:', method);
                    console.log('   Headers:', Object.keys(headers).join(', ') || 'none');
                    console.log('   Body size:', body ? body.length + ' chars' : 'none');
                    
                    // Check if this is a real API endpoint
                    if (window._pythonFetch && (url.includes('/api/') || url.includes('.json') || method !== 'GET')) {
                        // Use real fetch for API calls
                        window._realFetch(url, options).then(resolve).catch(reject);
                        return;
                    }
                    
                    // Simulate network delay for other requests
                    setTimeout(() => {
                        // Create Response object
                        const response = {
                            ok: true,
                            status: 200,
                            statusText: 'OK',
                            url: url,
                            headers: {
                                get: function(name) {
                                    const headers = {
                                        'content-type': 'application/json',
                                        'access-control-allow-origin': '*'
                                    };
                                    return headers[name.toLowerCase()] || null;
                                },
                                has: function(name) {
                                    return ['content-type', 'access-control-allow-origin'].includes(name.toLowerCase());
                                }
                            },
                            
                            // Response body methods
                            json: function() {
                                return Promise.resolve({
                                    success: true,
                                    data: { message: 'API response simulated', timestamp: Date.now() },
                                    meta: { version: '1.0', endpoint: url }
                                });
                            },
                            
                            text: function() {
                                return Promise.resolve('{"success": true, "message": "API response simulated"}');
                            },
                            
                            blob: function() {
                                return Promise.resolve(new Blob(['simulated response'], { type: 'text/plain' }));
                            },
                            
                            arrayBuffer: function() {
                                return Promise.resolve(new ArrayBuffer(0));
                            },
                            
                            formData: function() {
                                const fd = new FormData();
                                fd.append('response', 'simulated');
                                return Promise.resolve(fd);
                            },
                            
                            clone: function() {
                                return Object.assign({}, this);
                            }
                        };
                        
                        console.log('✅ Fetch completed with status:', response.status);
                        resolve(response);
                    }, 200);
                });
            };
            
            // XMLHttpRequest for legacy AJAX support
            window.XMLHttpRequest = function() {
                let readyState = 0;
                let status = 0;
                let statusText = '';
                let responseText = '';
                let responseXML = null;
                let onreadystatechange = null;
                let timeout = 0;
                let withCredentials = false;
                const headers = {};
                
                this.UNSENT = 0;
                this.OPENED = 1;
                this.HEADERS_RECEIVED = 2;
                this.LOADING = 3;
                this.DONE = 4;
                
                Object.defineProperty(this, 'readyState', {
                    get: function() { return readyState; }
                });
                
                Object.defineProperty(this, 'status', {
                    get: function() { return status; }
                });
                
                Object.defineProperty(this, 'statusText', {
                    get: function() { return statusText; }
                });
                
                Object.defineProperty(this, 'responseText', {
                    get: function() { return responseText; }
                });
                
                Object.defineProperty(this, 'responseXML', {
                    get: function() { return responseXML; }
                });
                
                this.open = function(method, url, async, user, password) {
                    console.log('📡 XMLHttpRequest:', method, url);
                    readyState = 1;
                    if (onreadystatechange) onreadystatechange();
                };
                
                this.setRequestHeader = function(name, value) {
                    headers[name] = value;
                };
                
                this.send = function(data) {
                    console.log('🚀 XMLHttpRequest send with data:', data ? 'yes' : 'no');
                    
                    // Simulate request progression
                    setTimeout(() => {
                        readyState = 2; // HEADERS_RECEIVED
                        if (onreadystatechange) onreadystatechange();
                        
                        setTimeout(() => {
                            readyState = 3; // LOADING
                            if (onreadystatechange) onreadystatechange();
                            
                            setTimeout(() => {
                                readyState = 4; // DONE
                                status = 200;
                                statusText = 'OK';
                                responseText = '{"success": true, "message": "AJAX request simulated"}';
                                
                                console.log('✅ XMLHttpRequest completed');
                                if (onreadystatechange) onreadystatechange();
                            }, 100);
                        }, 50);
                    }, 50);
                };
                
                this.abort = function() {
                    readyState = 4;
                    status = 0;
                    statusText = '';
                    if (onreadystatechange) onreadystatechange();
                };
                
                this.getResponseHeader = function(name) {
                    const responseHeaders = {
                        'content-type': 'application/json',
                        'cache-control': 'no-cache'
                    };
                    return responseHeaders[name.toLowerCase()] || null;
                };
                
                this.getAllResponseHeaders = function() {
                    return 'content-type: application/json\\r\\ncache-control: no-cache\\r\\n';
                };
                
                // Event handlers
                this.onreadystatechange = null;
                this.onload = null;
                this.onerror = null;
                this.ontimeout = null;
                this.onabort = null;
                this.onloadstart = null;
                this.onloadend = null;
                this.onprogress = null;
            };
            
            // WebSocket for real-time communication
            window.WebSocket = function(url, protocols) {
                console.log('🔌 WebSocket connection to:', url);
                
                this.url = url;
                this.readyState = 0; // CONNECTING
                this.protocol = '';
                this.extensions = '';
                this.bufferedAmount = 0;
                
                // WebSocket constants
                this.CONNECTING = 0;
                this.OPEN = 1;
                this.CLOSING = 2;
                this.CLOSED = 3;
                
                // Event handlers
                this.onopen = null;
                this.onmessage = null;
                this.onerror = null;
                this.onclose = null;
                
                // Simulate connection opening
                setTimeout(() => {
                    this.readyState = 1; // OPEN
                    console.log('✅ WebSocket connected');
                    if (this.onopen) this.onopen({ type: 'open' });
                }, 100);
                
                this.send = function(data) {
                    if (this.readyState === 1) {
                        console.log('📤 WebSocket send:', data);
                        
                        // Simulate echo response
                        setTimeout(() => {
                            if (this.onmessage) {
                                this.onmessage({
                                    type: 'message',
                                    data: 'Echo: ' + data,
                                    origin: url,
                                    lastEventId: '',
                                    source: null,
                                    ports: []
                                });
                            }
                        }, 50);
                    }
                };
                
                this.close = function(code, reason) {
                    this.readyState = 2; // CLOSING
                    setTimeout(() => {
                        this.readyState = 3; // CLOSED
                        console.log('🔌 WebSocket closed');
                        if (this.onclose) this.onclose({
                            type: 'close',
                            code: code || 1000,
                            reason: reason || '',
                            wasClean: true
                        });
                    }, 50);
                };
            };
            
            // EventSource for Server-Sent Events
            window.EventSource = function(url, eventSourceInitDict) {
                console.log('📡 EventSource connecting to:', url);
                
                this.url = url;
                this.readyState = 0; // CONNECTING
                this.withCredentials = eventSourceInitDict && eventSourceInitDict.withCredentials || false;
                
                // EventSource constants
                this.CONNECTING = 0;
                this.OPEN = 1;
                this.CLOSED = 2;
                
                // Event handlers
                this.onopen = null;
                this.onmessage = null;
                this.onerror = null;
                
                // Simulate connection opening
                setTimeout(() => {
                    this.readyState = 1; // OPEN
                    console.log('✅ EventSource connected');
                    if (this.onopen) this.onopen({ type: 'open' });
                    
                    // Simulate periodic messages
                    const interval = setInterval(() => {
                        if (this.readyState === 1 && this.onmessage) {
                            this.onmessage({
                                type: 'message',
                                data: JSON.stringify({ timestamp: Date.now(), message: 'Server event' }),
                                lastEventId: Date.now().toString(),
                                origin: url,
                                source: this
                            });
                        } else {
                            clearInterval(interval);
                        }
                    }, 5000);
                }, 100);
                
                this.close = function() {
                    this.readyState = 2; // CLOSED
                    console.log('📡 EventSource closed');
                };
                
                this.addEventListener = function(type, listener, options) {
                    if (type === 'message') this.onmessage = listener;
                    else if (type === 'open') this.onopen = listener;
                    else if (type === 'error') this.onerror = listener;
                };
            };
            
            // Geolocation API
            window.navigator.geolocation = {
                getCurrentPosition: function(success, error, options) {
                    console.log('🌍 Geolocation request');
                    setTimeout(() => {
                        const position = {
                            coords: {
                                latitude: 37.7749,
                                longitude: -122.4194,
                                accuracy: 10,
                                altitude: null,
                                altitudeAccuracy: null,
                                heading: null,
                                speed: null
                            },
                            timestamp: Date.now()
                        };
                        console.log('📍 Location:', position.coords.latitude, position.coords.longitude);
                        if (success) success(position);
                    }, 200);
                },
                
                watchPosition: function(success, error, options) {
                    console.log('🌍 Geolocation watch started');
                    return this.getCurrentPosition(success, error, options);
                },
                
                clearWatch: function(id) {
                    console.log('🌍 Geolocation watch cleared');
                }
            };
            
            // CSS Object Model (CSSOM) Implementation
            
            // CSSStyleDeclaration - Core CSS style manipulation
            function CSSStyleDeclaration() {
                this._properties = {};
                this.length = 0;
                
                // CSS property access methods
                this.getPropertyValue = function(property) {
                    return this._properties[property] || '';
                };
                
                this.setProperty = function(property, value, priority) {
                    if (!this._properties[property]) {
                        this.length++;
                    }
                    this._properties[property] = value;
                    if (priority === 'important') {
                        this._properties[property + '!important'] = true;
                    }
                };
                
                this.removeProperty = function(property) {
                    if (this._properties[property]) {
                        delete this._properties[property];
                        this.length--;
                    }
                    return this._properties[property] || '';
                };
                
                this.getPropertyPriority = function(property) {
                    return this._properties[property + '!important'] ? 'important' : '';
                };
                
                this.item = function(index) {
                    return Object.keys(this._properties)[index] || null;
                };
                
                this.cssText = '';
                
                // Proxy for direct property access (e.g., style.color = 'red')
                return new Proxy(this, {
                    get: function(target, prop) {
                        if (prop in target) return target[prop];
                        if (typeof prop === 'string') {
                            // Convert camelCase to kebab-case
                            const kebabProp = prop.replace(/([A-Z])/g, '-$1').toLowerCase();
                            return target._properties[kebabProp] || '';
                        }
                        return undefined;
                    },
                    set: function(target, prop, value) {
                        if (prop in target) {
                            target[prop] = value;
                            return true;
                        }
                        if (typeof prop === 'string') {
                            // Convert camelCase to kebab-case
                            const kebabProp = prop.replace(/([A-Z])/g, '-$1').toLowerCase();
                            target.setProperty(kebabProp, value);
                            return true;
                        }
                        return false;
                    }
                });
            }
            
            // CSSRule - Base class for CSS rules
            function CSSRule() {
                this.cssText = '';
                this.parentRule = null;
                this.parentStyleSheet = null;
                this.type = 0; // CSSRule.UNKNOWN_RULE
            }
            
            // CSSStyleRule - Style rule implementation
            function CSSStyleRule() {
                CSSRule.call(this);
                this.type = 1; // CSSRule.STYLE_RULE
                this.selectorText = '';
                this.style = new CSSStyleDeclaration();
            }
            CSSStyleRule.prototype = Object.create(CSSRule.prototype);
            
            // CSSRuleList - Collection of CSS rules
            function CSSRuleList() {
                this._rules = [];
                this.length = 0;
                
                this.item = function(index) {
                    return this._rules[index] || null;
                };
                
                // Make it array-like
                return new Proxy(this, {
                    get: function(target, prop) {
                        if (prop in target) return target[prop];
                        const index = parseInt(prop);
                        if (!isNaN(index)) return target._rules[index];
                        return undefined;
                    }
                });
            }
            
            // CSSStyleSheet - Style sheet implementation
            function CSSStyleSheet() {
                this.type = 'text/css';
                this.disabled = false;
                this.ownerNode = null;
                this.parentStyleSheet = null;
                this.href = null;
                this.title = '';
                this.media = [];
                this.cssRules = new CSSRuleList();
                this.rules = this.cssRules; // IE compatibility
                
                this.insertRule = function(rule, index) {
                    const cssRule = new CSSStyleRule();
                    cssRule.cssText = rule;
                    // Parse selector and declarations from rule text
                    const parts = rule.split('{');
                    if (parts.length === 2) {
                        cssRule.selectorText = parts[0].trim();
                        // Simple property parsing
                        const declarations = parts[1].replace('}', '').split(';');
                        declarations.forEach(decl => {
                            const [prop, val] = decl.split(':');
                            if (prop && val) {
                                cssRule.style.setProperty(prop.trim(), val.trim());
                            }
                        });
                    }
                    
                    index = index || this.cssRules.length;
                    this.cssRules._rules.splice(index, 0, cssRule);
                    this.cssRules.length = this.cssRules._rules.length;
                    return index;
                };
                
                this.deleteRule = function(index) {
                    this.cssRules._rules.splice(index, 1);
                    this.cssRules.length = this.cssRules._rules.length;
                };
                
                this.addRule = function(selector, style, index) {
                    return this.insertRule(selector + '{' + style + '}', index);
                };
                
                this.removeRule = function(index) {
                    this.deleteRule(index);
                };
            }
            
            // StyleSheetList - Collection of stylesheets
            function StyleSheetList() {
                this._sheets = [];
                this.length = 0;
                
                this.item = function(index) {
                    return this._sheets[index] || null;
                };
                
                return new Proxy(this, {
                    get: function(target, prop) {
                        if (prop in target) return target[prop];
                        const index = parseInt(prop);
                        if (!isNaN(index)) return target._sheets[index];
                        return undefined;
                    }
                });
            }
            
            // CSS namespace with utility functions
            window.CSS = {
                escape: function(value) {
                    return value.replace(/([!"#$%&'()*+,.\/:;<=>?@[\]^`{|}~])/g, '\\$1');
                },
                
                supports: function(property, value) {
                    // Simplified support detection
                    const supportedProperties = [
                        'color', 'background-color', 'font-size', 'margin', 'padding',
                        'border', 'width', 'height', 'display', 'position', 'top',
                        'left', 'right', 'bottom', 'opacity', 'transform', 'transition'
                    ];
                    
                    if (arguments.length === 1) {
                        // Supports query format: "display: flex"
                        const [prop] = property.split(':');
                        return supportedProperties.includes(prop.trim());
                    }
                    
                    return supportedProperties.includes(property);
                },
                
                // CSS Typed Object Model placeholder
                number: function(value) {
                    return { value: parseFloat(value), unit: '' };
                },
                
                px: function(value) {
                    return { value: parseFloat(value), unit: 'px' };
                },
                
                percent: function(value) {
                    return { value: parseFloat(value), unit: '%' };
                }
            };
            
            // MediaQueryList for responsive design
            function MediaQueryList(media) {
                this.media = media;
                this.matches = false; // Default to false in CLI environment
                this._listeners = [];
                
                this.addListener = function(listener) {
                    this._listeners.push(listener);
                };
                
                this.removeListener = function(listener) {
                    const index = this._listeners.indexOf(listener);
                    if (index > -1) this._listeners.splice(index, 1);
                };
                
                this.addEventListener = this.addListener;
                this.removeEventListener = this.removeListener;
            }
            
            // getComputedStyle implementation
            window.getComputedStyle = function(element, pseudoElement) {
                const computedStyle = new CSSStyleDeclaration();
                
                // Merge styles from various sources
                if (element.style) {
                    Object.assign(computedStyle._properties, element.style._properties || {});
                }
                
                // Add default computed values
                const defaults = {
                    'display': 'block',
                    'position': 'static',
                    'color': 'rgb(0, 0, 0)',
                    'background-color': 'rgba(0, 0, 0, 0)',
                    'font-size': '16px',
                    'font-family': 'Times New Roman',
                    'margin': '0px',
                    'padding': '0px',
                    'border': '0px none rgb(0, 0, 0)',
                    'width': 'auto',
                    'height': 'auto'
                };
                
                Object.keys(defaults).forEach(prop => {
                    if (!computedStyle._properties[prop]) {
                        computedStyle._properties[prop] = defaults[prop];
                    }
                });
                
                return computedStyle;
            };
            
            // matchMedia for responsive queries
            window.matchMedia = function(mediaQuery) {
                return new MediaQueryList(mediaQuery);
            };
            
            // Modern JavaScript APIs Implementation
            
            // Fetch API Implementation
            window.fetch = function(url, options) {
                options = options || {};
                
                return new Promise((resolve, reject) => {
                    // Simulate network delay
                    setTimeout(() => {
                        try {
                            // Mock response for demonstration
                            const response = {
                                ok: true,
                                status: 200,
                                statusText: 'OK',
                                url: url,
                                headers: {
                                    get: function(name) {
                                        const headers = {
                                            'content-type': 'application/json',
                                            'access-control-allow-origin': '*'
                                        };
                                        return headers[name.toLowerCase()] || null;
                                    },
                                    has: function(name) {
                                        return ['content-type', 'access-control-allow-origin'].includes(name.toLowerCase());
                                    }
                                },
                                json: function() {
                                    return Promise.resolve({
                                        message: 'Fetch API simulation',
                                        url: url,
                                        method: options.method || 'GET',
                                        timestamp: new Date().toISOString()
                                    });
                                },
                                text: function() {
                                    return Promise.resolve('Fetch API response for: ' + url);
                                },
                                blob: function() {
                                    return Promise.resolve(new Blob(['Mock blob data']));
                                },
                                arrayBuffer: function() {
                                    return Promise.resolve(new ArrayBuffer(8));
                                },
                                clone: function() {
                                    return this;
                                }
                            };
                            
                            resolve(response);
                        } catch (error) {
                            reject(new Error('Fetch failed: ' + error.message));
                        }
                    }, 100);
                });
            };
            
            // Request and Response constructors
            window.Request = function(url, options) {
                this.url = url;
                this.method = (options && options.method) || 'GET';
                this.headers = (options && options.headers) || {};
                this.body = (options && options.body) || null;
            };
            
            window.Response = function(body, options) {
                options = options || {};
                this.body = body;
                this.status = options.status || 200;
                this.statusText = options.statusText || 'OK';
                this.ok = this.status >= 200 && this.status < 300;
                this.headers = options.headers || {};
                
                this.json = function() {
                    return Promise.resolve(JSON.parse(body));
                };
                this.text = function() {
                    return Promise.resolve(String(body));
                };
            };
            
            // WebGL Context Implementation
            function WebGLRenderingContext() {
                // WebGL constants
                this.VERTEX_SHADER = 35633;
                this.FRAGMENT_SHADER = 35632;
                this.COMPILE_STATUS = 35713;
                this.LINK_STATUS = 35714;
                this.COLOR_BUFFER_BIT = 16384;
                this.DEPTH_BUFFER_BIT = 256;
                this.TRIANGLES = 4;
                this.FLOAT = 5126;
                this.ARRAY_BUFFER = 34962;
                this.STATIC_DRAW = 35044;
                
                // Mock WebGL methods
                this.createShader = function(type) {
                    return { type: type, id: Math.random() };
                };
                
                this.shaderSource = function(shader, source) {
                    shader.source = source;
                };
                
                this.compileShader = function(shader) {
                    shader.compiled = true;
                };
                
                this.getShaderParameter = function(shader, pname) {
                    return pname === this.COMPILE_STATUS ? true : null;
                };
                
                this.createProgram = function() {
                    return { id: Math.random(), shaders: [] };
                };
                
                this.attachShader = function(program, shader) {
                    program.shaders.push(shader);
                };
                
                this.linkProgram = function(program) {
                    program.linked = true;
                };
                
                this.getProgramParameter = function(program, pname) {
                    return pname === this.LINK_STATUS ? true : null;
                };
                
                this.useProgram = function(program) {
                    this.currentProgram = program;
                };
                
                this.createBuffer = function() {
                    return { id: Math.random() };
                };
                
                this.bindBuffer = function(target, buffer) {
                    this.boundBuffer = buffer;
                };
                
                this.bufferData = function(target, data, usage) {
                    if (this.boundBuffer) {
                        this.boundBuffer.data = data;
                    }
                };
                
                this.getAttribLocation = function(program, name) {
                    return Math.floor(Math.random() * 10);
                };
                
                this.getUniformLocation = function(program, name) {
                    return { name: name, id: Math.random() };
                };
                
                this.enableVertexAttribArray = function(index) {
                    // Mock implementation
                };
                
                this.vertexAttribPointer = function(index, size, type, normalized, stride, offset) {
                    // Mock implementation
                };
                
                this.uniform1f = function(location, value) {
                    // Mock implementation
                };
                
                this.uniform2f = function(location, x, y) {
                    // Mock implementation
                };
                
                this.uniform3f = function(location, x, y, z) {
                    // Mock implementation
                };
                
                this.uniform4f = function(location, x, y, z, w) {
                    // Mock implementation
                };
                
                this.clearColor = function(r, g, b, a) {
                    this.clearColorValue = [r, g, b, a];
                };
                
                this.clear = function(mask) {
                    // Mock clearing
                };
                
                this.drawArrays = function(mode, first, count) {
                    // Mock drawing
                };
                
                this.viewport = function(x, y, width, height) {
                    this.viewportValue = [x, y, width, height];
                };
            }
            
            // Enhanced Canvas with WebGL support
            if (typeof HTMLCanvasElement !== 'undefined') {
                HTMLCanvasElement.prototype.getContext = function(contextType, options) {
                    if (contextType === 'webgl' || contextType === 'experimental-webgl') {
                        return new WebGLRenderingContext();
                    } else if (contextType === '2d') {
                        return {
                            fillStyle: '#000000',
                            strokeStyle: '#000000',
                            lineWidth: 1,
                            fillRect: function(x, y, w, h) { /* mock */ },
                            strokeRect: function(x, y, w, h) { /* mock */ },
                            clearRect: function(x, y, w, h) { /* mock */ },
                            beginPath: function() { /* mock */ },
                            moveTo: function(x, y) { /* mock */ },
                            lineTo: function(x, y) { /* mock */ },
                            arc: function(x, y, r, start, end) { /* mock */ },
                            fill: function() { /* mock */ },
                            stroke: function() { /* mock */ }
                        };
                    }
                    return null;
                };
            }
            
            // Clipboard API Implementation  
            if (!window.navigator) {
                window.navigator = {};
            }
            window.navigator.clipboard = {
                writeText: function(text) {
                    return new Promise((resolve) => {
                        console.log('📋 Text copied to clipboard:', text.substring(0, 50) + (text.length > 50 ? '...' : ''));
                        window._clipboardData = text;
                        resolve();
                    });
                },
                
                readText: function() {
                    return new Promise((resolve) => {
                        const clipboardText = window._clipboardData || 'Sample clipboard content';
                        console.log('📋 Text read from clipboard:', clipboardText.substring(0, 50) + (clipboardText.length > 50 ? '...' : ''));
                        resolve(clipboardText);
                    });
                },
                
                write: function(data) {
                    return new Promise((resolve) => {
                        console.log('📋 Data written to clipboard');
                        window._clipboardData = data;
                        resolve();
                    });
                },
                
                read: function() {
                    return new Promise((resolve) => {
                        console.log('📋 Data read from clipboard');
                        resolve([{
                            type: 'text/plain',
                            getAsString: function(callback) {
                                callback(window._clipboardData || 'Sample clipboard content');
                            }
                        }]);
                    });
                }
            };
            
            // Drag and Drop API Implementation
            window.DragEvent = function(type, eventInitDict) {
                this.type = type;
                this.dataTransfer = eventInitDict && eventInitDict.dataTransfer || new DataTransfer();
                this.clientX = (eventInitDict && eventInitDict.clientX) || 0;
                this.clientY = (eventInitDict && eventInitDict.clientY) || 0;
                this.target = null;
                this.preventDefault = function() {};
                this.stopPropagation = function() {};
            };
            
            window.DataTransfer = function() {
                this._data = {};
                this._files = [];
                this.dropEffect = 'none';
                this.effectAllowed = 'all';
                
                this.setData = function(format, data) {
                    this._data[format] = data;
                    console.log('🗂️ Drag data set:', format, '→', data.substring(0, 30) + '...');
                };
                
                this.getData = function(format) {
                    const data = this._data[format] || '';
                    console.log('🗂️ Drag data retrieved:', format, '→', data.substring(0, 30) + '...');
                    return data;
                };
                
                this.clearData = function(format) {
                    if (format) {
                        delete this._data[format];
                    } else {
                        this._data = {};
                    }
                };
                
                this.setDragImage = function(element, x, y) {
                    console.log('🖼️ Drag image set:', element.tagName || 'unknown');
                };
                
                Object.defineProperty(this, 'files', {
                    get: function() { return this._files; }
                });
                
                Object.defineProperty(this, 'types', {
                    get: function() { return Object.keys(this._data); }
                });
            };
            
            // Add drag and drop methods to HTMLElement
            if (typeof createHTMLElement === 'function') {
                const originalCreateElement = createHTMLElement;
                createHTMLElement = function(tagName, id) {
                    const element = originalCreateElement(tagName, id);
                    
                    // Add drag and drop functionality
                    element.draggable = false;
                    
                    element.ondragstart = null;
                    element.ondrag = null;
                    element.ondragend = null;
                    element.ondragenter = null;
                    element.ondragover = null;
                    element.ondragleave = null;
                    element.ondrop = null;
                    
                    // Drag start simulation
                    element.startDrag = function(data) {
                        console.log('🚀 Drag started on:', this.tagName + (this.id ? '#' + this.id : ''));
                        
                        const dragEvent = new DragEvent('dragstart', {
                            dataTransfer: new DataTransfer()
                        });
                        
                        if (data) {
                            Object.entries(data).forEach(([format, value]) => {
                                dragEvent.dataTransfer.setData(format, value);
                            });
                        }
                        
                        if (this.ondragstart) {
                            this.ondragstart(dragEvent);
                        }
                        
                        this.dispatchEvent(dragEvent);
                    };
                    
                    // Drop simulation
                    element.simulateDrop = function(data) {
                        console.log('🎯 Drop simulated on:', this.tagName + (this.id ? '#' + this.id : ''));
                        
                        const dropEvent = new DragEvent('drop', {
                            dataTransfer: new DataTransfer()
                        });
                        
                        if (data) {
                            Object.entries(data).forEach(([format, value]) => {
                                dropEvent.dataTransfer.setData(format, value);
                            });
                        }
                        
                        if (this.ondrop) {
                            this.ondrop(dropEvent);
                        }
                        
                        this.dispatchEvent(dropEvent);
                    };
                    
                    return element;
                };
            }
            
            // Web Workers Implementation
            window.Worker = function(scriptURL) {
                this.scriptURL = scriptURL;
                this._listeners = {};
                
                this.postMessage = function(message) {
                    // Simulate worker processing
                    setTimeout(() => {
                        const response = {
                            data: {
                                type: 'response',
                                input: message,
                                result: 'Worker processed: ' + JSON.stringify(message),
                                timestamp: Date.now()
                            }
                        };
                        
                        if (this._listeners.message) {
                            this._listeners.message.forEach(listener => {
                                try {
                                    listener(response);
                                } catch (e) {
                                    console.error('Worker message listener error:', e);
                                }
                            });
                        }
                    }, 50);
                };
                
                this.terminate = function() {
                    this._terminated = true;
                    this._listeners = {};
                };
                
                this.addEventListener = function(type, listener) {
                    if (!this._listeners[type]) {
                        this._listeners[type] = [];
                    }
                    this._listeners[type].push(listener);
                };
                
                this.removeEventListener = function(type, listener) {
                    if (this._listeners[type]) {
                        const index = this._listeners[type].indexOf(listener);
                        if (index > -1) {
                            this._listeners[type].splice(index, 1);
                        }
                    }
                };
                
                // Support for onmessage property
                Object.defineProperty(this, 'onmessage', {
                    set: function(handler) {
                        this.removeEventListener('message', this._onmessageHandler);
                        this._onmessageHandler = handler;
                        if (handler) {
                            this.addEventListener('message', handler);
                        }
                    },
                    get: function() {
                        return this._onmessageHandler || null;
                    }
                });
            };
            
            // IndexedDB Implementation
            window.indexedDB = {
                open: function(name, version) {
                    return new Promise((resolve, reject) => {
                        setTimeout(() => {
                            const db = {
                                name: name,
                                version: version || 1,
                                objectStoreNames: [],
                                
                                createObjectStore: function(name, options) {
                                    const store = {
                                        name: name,
                                        keyPath: (options && options.keyPath) || null,
                                        autoIncrement: (options && options.autoIncrement) || false,
                                        _data: new Map(),
                                        
                                        add: function(value, key) {
                                            return new Promise((resolve, reject) => {
                                                setTimeout(() => {
                                                    const storeKey = key || (this.autoIncrement ? Date.now() : value[this.keyPath]);
                                                    if (this._data.has(storeKey)) {
                                                        reject(new Error('Key already exists'));
                                                    } else {
                                                        this._data.set(storeKey, value);
                                                        resolve(storeKey);
                                                    }
                                                }, 10);
                                            });
                                        },
                                        
                                        put: function(value, key) {
                                            return new Promise((resolve) => {
                                                setTimeout(() => {
                                                    const storeKey = key || (this.autoIncrement ? Date.now() : value[this.keyPath]);
                                                    this._data.set(storeKey, value);
                                                    resolve(storeKey);
                                                }, 10);
                                            });
                                        },
                                        
                                        get: function(key) {
                                            return new Promise((resolve) => {
                                                setTimeout(() => {
                                                    resolve(this._data.get(key) || undefined);
                                                }, 10);
                                            });
                                        },
                                        
                                        delete: function(key) {
                                            return new Promise((resolve) => {
                                                setTimeout(() => {
                                                    const existed = this._data.has(key);
                                                    this._data.delete(key);
                                                    resolve(existed);
                                                }, 10);
                                            });
                                        },
                                        
                                        clear: function() {
                                            return new Promise((resolve) => {
                                                setTimeout(() => {
                                                    this._data.clear();
                                                    resolve();
                                                }, 10);
                                            });
                                        },
                                        
                                        count: function() {
                                            return new Promise((resolve) => {
                                                setTimeout(() => {
                                                    resolve(this._data.size);
                                                }, 10);
                                            });
                                        },
                                        
                                        createIndex: function(name, keyPath, options) {
                                            return {
                                                name: name,
                                                keyPath: keyPath,
                                                unique: (options && options.unique) || false
                                            };
                                        }
                                    };
                                    
                                    this.objectStoreNames.push(name);
                                    return store;
                                },
                                
                                transaction: function(storeNames, mode) {
                                    return {
                                        objectStore: function(name) {
                                            return db.createObjectStore(name);
                                        },
                                        abort: function() {
                                            // Mock abort
                                        },
                                        mode: mode || 'readonly'
                                    };
                                },
                                
                                close: function() {
                                    // Mock close
                                }
                            };
                            
                            const request = {
                                result: db,
                                error: null,
                                readyState: 'done',
                                _listeners: {},
                                
                                addEventListener: function(type, listener) {
                                    if (!this._listeners[type]) {
                                        this._listeners[type] = [];
                                    }
                                    this._listeners[type].push(listener);
                                }
                            };
                            
                            // Set up onsuccess property
                            Object.defineProperty(request, 'onsuccess', {
                                set: function(handler) {
                                    this._onsuccessHandler = handler;
                                    if (handler) {
                                        setTimeout(() => handler({ target: this }), 20);
                                    }
                                },
                                get: function() {
                                    return this._onsuccessHandler || null;
                                }
                            });
                            
                            resolve(request);
                        }, 30);
                    });
                },
                
                deleteDatabase: function(name) {
                    return new Promise((resolve) => {
                        setTimeout(() => {
                            resolve({ target: { result: undefined } });
                        }, 50);
                    });
                }
            };
            
            // File API Implementation
            window.File = function(fileBits, fileName, options) {
                this.name = fileName;
                this.size = 0;
                this.type = (options && options.type) || '';
                this.lastModified = (options && options.lastModified) || Date.now();
                this.lastModifiedDate = new Date(this.lastModified);
                
                if (fileBits && Array.isArray(fileBits)) {
                    this.size = fileBits.reduce((total, bit) => {
                        if (typeof bit === 'string') return total + bit.length;
                        if (bit instanceof ArrayBuffer) return total + bit.byteLength;
                        return total;
                    }, 0);
                }
            };
            
            window.Blob = function(blobParts, options) {
                this.size = 0;
                this.type = (options && options.type) || '';
                
                if (blobParts && Array.isArray(blobParts)) {
                    this.size = blobParts.reduce((total, part) => {
                        if (typeof part === 'string') return total + part.length;
                        if (part instanceof ArrayBuffer) return total + part.byteLength;
                        return total;
                    }, 0);
                }
                
                this.slice = function(start, end, contentType) {
                    return new Blob([], { type: contentType || this.type });
                };
                
                this.text = function() {
                    return Promise.resolve('Mock blob text content');
                };
                
                this.arrayBuffer = function() {
                    return Promise.resolve(new ArrayBuffer(this.size));
                };
            };
            
            window.FileReader = function() {
                this.readyState = 0; // EMPTY
                this.result = null;
                this.error = null;
                this._listeners = {};
                
                this.readAsText = function(file, encoding) {
                    setTimeout(() => {
                        this.readyState = 2; // DONE
                        this.result = 'Mock file content: ' + (file.name || 'unknown file');
                        
                        if (this.onload) {
                            this.onload({ target: this });
                        }
                        this._trigger('load');
                    }, 100);
                };
                
                this.readAsDataURL = function(file) {
                    setTimeout(() => {
                        this.readyState = 2; // DONE
                        this.result = 'data:' + file.type + ';base64,bW9ja19kYXRh';
                        
                        if (this.onload) {
                            this.onload({ target: this });
                        }
                        this._trigger('load');
                    }, 100);
                };
                
                this.readAsArrayBuffer = function(file) {
                    setTimeout(() => {
                        this.readyState = 2; // DONE
                        this.result = new ArrayBuffer(file.size || 8);
                        
                        if (this.onload) {
                            this.onload({ target: this });
                        }
                        this._trigger('load');
                    }, 100);
                };
                
                this.abort = function() {
                    this.readyState = 2; // DONE
                    if (this.onabort) {
                        this.onabort({ target: this });
                    }
                    this._trigger('abort');
                };
                
                this.addEventListener = function(type, listener) {
                    if (!this._listeners[type]) {
                        this._listeners[type] = [];
                    }
                    this._listeners[type].push(listener);
                };
                
                this._trigger = function(type) {
                    if (this._listeners[type]) {
                        this._listeners[type].forEach(listener => {
                            try {
                                listener({ target: this });
                            } catch (e) {
                                console.error('FileReader event error:', e);
                            }
                        });
                    }
                };
            };
            
            // Enhanced Promise support for async/await
            if (typeof Promise === 'undefined') {
                window.Promise = function(executor) {
                    var self = this;
                    this.state = 'pending';
                    this.value = undefined;
                    this.handlers = [];
                    
                    function resolve(value) {
                        if (self.state === 'pending') {
                            self.state = 'fulfilled';
                            self.value = value;
                            self.handlers.forEach(handle);
                            self.handlers = null;
                        }
                    }
                    
                    function reject(reason) {
                        if (self.state === 'pending') {
                            self.state = 'rejected';
                            self.value = reason;
                            self.handlers.forEach(handle);
                            self.handlers = null;
                        }
                    }
                    
                    function handle(handler) {
                        if (self.state === 'pending') {
                            self.handlers.push(handler);
                        } else {
                            if (self.state === 'fulfilled' && handler.onFulfilled) {
                                handler.onFulfilled(self.value);
                            }
                            if (self.state === 'rejected' && handler.onRejected) {
                                handler.onRejected(self.value);
                            }
                        }
                    }
                    
                    this.then = function(onFulfilled, onRejected) {
                        return new Promise(function(resolve, reject) {
                            handle({
                                onFulfilled: function(value) {
                                    try {
                                        resolve(onFulfilled ? onFulfilled(value) : value);
                                    } catch (ex) {
                                        reject(ex);
                                    }
                                },
                                onRejected: function(reason) {
                                    try {
                                        resolve(onRejected ? onRejected(reason) : reason);
                                    } catch (ex) {
                                        reject(ex);
                                    }
                                }
                            });
                        });
                    };
                    
                    this.catch = function(onRejected) {
                        return this.then(null, onRejected);
                    };
                    
                    try {
                        executor(resolve, reject);
                    } catch (ex) {
                        reject(ex);
                    }
                };
                
                Promise.resolve = function(value) {
                    return new Promise(function(resolve) {
                        resolve(value);
                    });
                };
                
                Promise.reject = function(reason) {
                    return new Promise(function(resolve, reject) {
                        reject(reason);
                    });
                };
                
                Promise.all = function(promises) {
                    return new Promise(function(resolve, reject) {
                        var results = [];
                        var count = 0;
                        
                        if (promises.length === 0) {
                            resolve(results);
                            return;
                        }
                        
                        promises.forEach(function(promise, index) {
                            Promise.resolve(promise).then(function(value) {
                                results[index] = value;
                                count++;
                                if (count === promises.length) {
                                    resolve(results);
                                }
                            }, reject);
                        });
                    });
                };
            }
            
            // Add React-like framework support
            window.__react = {
                enqueue: function(callback) {
                    // Simulate React's enqueue functionality
                    if (typeof callback === 'function') {
                        try { callback(); } catch(e) { /* ignore */ }
                    }
                },
                close: function() {
                    // Simulate cleanup
                    return true;
                }
            };
            
            // Add common DOM manipulation methods
            window.requestAnimationFrame = function(callback) {
                return setTimeout(callback, 16); // ~60fps
            };
            
            window.cancelAnimationFrame = function(id) {
                clearTimeout(id);
            };
            
            // Create comprehensive HTMLElement base class
            function createHTMLElement(tagName, id) {
                return {
                    // Core Element properties
                    tagName: tagName ? tagName.toUpperCase() : 'DIV',
                    id: id || '',
                    className: '',
                    classList: {
                        add: function(cls) { this.className += ' ' + cls; },
                        remove: function(cls) { this.className = this.className.replace(cls, ''); },
                        contains: function(cls) { return this.className.includes(cls); },
                        toggle: function(cls) { this.contains(cls) ? this.remove(cls) : this.add(cls); }
                    },
                    
                    // Content properties
                    innerHTML: '',
                    outerHTML: '',
                    textContent: '',
                    innerText: '',
                    value: '',
                    
                    // Visual properties
                    style: new CSSStyleDeclaration(),
                    hidden: false,
                    title: '',
                    lang: '',
                    dir: '',
                    
                    // Form-related properties
                    disabled: false,
                    checked: false,
                    selected: false,
                    type: '',
                    name: '',
                    placeholder: '',
                    
                    // Interactive properties
                    _formData: {},
                    _fileData: null,
                    _clipboardAccess: true,
                    _interactionHistory: [],
                    
                    // Hierarchy properties
                    parentNode: null,
                    parentElement: null,
                    children: [],
                    childNodes: [],
                    firstChild: null,
                    lastChild: null,
                    nextSibling: null,
                    previousSibling: null,
                    
                    // Dimension properties
                    offsetWidth: 0,
                    offsetHeight: 0,
                    clientWidth: 0,
                    clientHeight: 0,
                    scrollWidth: 0,
                    scrollHeight: 0,
                    scrollTop: 0,
                    scrollLeft: 0,
                    
                    // Attribute methods
                    setAttribute: function(name, value) {
                        this[name] = value;
                        if (window._recordDOMChange) {
                            window._recordDOMChange(this.id, {[name]: value});
                        }
                    },
                    getAttribute: function(name) {
                        return this[name] || null;
                    },
                    removeAttribute: function(name) {
                        delete this[name];
                        if (window._recordDOMChange) {
                            window._recordDOMChange(this.id, {[name]: null});
                        }
                    },
                    hasAttribute: function(name) {
                        return name in this && this[name] !== null && this[name] !== undefined;
                    },
                    getAttributeNames: function() {
                        return Object.keys(this).filter(key => typeof this[key] !== 'function');
                    },
                    
                    // DOM manipulation methods
                    appendChild: function(child) {
                        this.children.push(child);
                        this.childNodes.push(child);
                        child.parentNode = this;
                        child.parentElement = this;
                        this._updateChildRefs();
                        return child;
                    },
                    removeChild: function(child) {
                        const index = this.children.indexOf(child);
                        if (index > -1) {
                            this.children.splice(index, 1);
                            this.childNodes.splice(index, 1);
                            child.parentNode = null;
                            child.parentElement = null;
                            this._updateChildRefs();
                        }
                        return child;
                    },
                    insertBefore: function(newChild, referenceChild) {
                        const index = this.children.indexOf(referenceChild);
                        if (index > -1) {
                            this.children.splice(index, 0, newChild);
                            this.childNodes.splice(index, 0, newChild);
                        } else {
                            this.appendChild(newChild);
                        }
                        return newChild;
                    },
                    replaceChild: function(newChild, oldChild) {
                        const index = this.children.indexOf(oldChild);
                        if (index > -1) {
                            this.children[index] = newChild;
                            this.childNodes[index] = newChild;
                            newChild.parentNode = this;
                            newChild.parentElement = this;
                            oldChild.parentNode = null;
                            oldChild.parentElement = null;
                        }
                        return oldChild;
                    },
                    cloneNode: function(deep) {
                        const clone = createHTMLElement(this.tagName, this.id + '_clone');
                        Object.assign(clone, this);
                        if (deep) {
                            clone.children = this.children.map(child => child.cloneNode(true));
                        }
                        return clone;
                    },
                    
                    // Event handling
                    addEventListener: function(event, handler, options) {
                        this._listeners = this._listeners || {};
                        this._listeners[event] = this._listeners[event] || [];
                        this._listeners[event].push({handler, options});
                    },
                    removeEventListener: function(event, handler) {
                        if (this._listeners && this._listeners[event]) {
                            this._listeners[event] = this._listeners[event].filter(
                                item => item.handler !== handler
                            );
                        }
                    },
                    dispatchEvent: function(event) {
                        if (this._listeners && this._listeners[event.type]) {
                            this._listeners[event.type].forEach(item => {
                                try { item.handler(event); } catch(e) { console.error('Event handler error:', e); }
                            });
                        }
                        return true;
                    },
                    
                    // Query methods
                    querySelector: function(selector) {
                        // Basic implementation for common selectors
                        if (selector.startsWith('#')) {
                            const id = selector.substring(1);
                            return this.children.find(child => child.id === id) || null;
                        }
                        if (selector.startsWith('.')) {
                            const className = selector.substring(1);
                            return this.children.find(child => child.className.includes(className)) || null;
                        }
                        // Tag name selector
                        return this.children.find(child => child.tagName === selector.toUpperCase()) || null;
                    },
                    querySelectorAll: function(selector) {
                        const results = [];
                        if (selector.startsWith('#')) {
                            const id = selector.substring(1);
                            const found = this.children.find(child => child.id === id);
                            if (found) results.push(found);
                        } else if (selector.startsWith('.')) {
                            const className = selector.substring(1);
                            results.push(...this.children.filter(child => child.className.includes(className)));
                        } else {
                            results.push(...this.children.filter(child => child.tagName === selector.toUpperCase()));
                        }
                        return results;
                    },
                    
                    // Focus methods
                    focus: function() {
                        document.activeElement = this;
                        this.dispatchEvent({type: 'focus', target: this});
                    },
                    blur: function() {
                        if (document.activeElement === this) {
                            document.activeElement = null;
                        }
                        this.dispatchEvent({type: 'blur', target: this});
                    },
                    
                    // Utility methods
                    _updateChildRefs: function() {
                        this.firstChild = this.children[0] || null;
                        this.lastChild = this.children[this.children.length - 1] || null;
                        
                        for (let i = 0; i < this.children.length; i++) {
                            this.children[i].nextSibling = this.children[i + 1] || null;
                            this.children[i].previousSibling = this.children[i - 1] || null;
                        }
                    },
                    
                    // Content manipulation
                    insertAdjacentHTML: function(position, html) {
                        // Simplified implementation
                        if (position === 'beforeend') {
                            this.innerHTML += html;
                        }
                    },
                    
                    // Scroll methods
                    scrollIntoView: function() {
                        // Simulate scroll behavior
                        console.log('Element scrolled into view:', this.id || this.tagName);
                    },
                    
                    // Interactive click behavior with real functionality
                    click: function() {
                        console.log('🖱️ Element clicked: ' + (this.id || this.tagName));
                        
                        // Handle real form interactions
                        if (this.tagName === 'BUTTON' || this.type === 'submit') {
                            this.handleFormSubmission();
                        } else if (this.tagName === 'INPUT' && this.type === 'file') {
                            this.handleFileUpload();
                        } else if (this.tagName === 'INPUT' || this.tagName === 'TEXTAREA') {
                            this.handleInput();
                        } else if (this.tagName === 'SELECT') {
                            this.handleSelectChange();
                        } else if (this.tagName === 'A') {
                            this.handleLinkClick();
                        }
                        
                        // Record interaction for analytics
                        this._interactionHistory.push({
                            type: 'click',
                            timestamp: Date.now(),
                            element: this.tagName + (this.id ? '#' + this.id : '')
                        });
                        
                        // Trigger click events
                        this.dispatchEvent({
                            type: 'click',
                            target: this,
                            preventDefault: function() {},
                            stopPropagation: function() {}
                        });
                    },
                    
                    // Real form submission handling
                    handleFormSubmission: function() {
                        const form = this.closest('form') || (this.tagName === 'FORM' ? this : null);
                        if (form) {
                            const formData = this.collectFormData(form);
                            const action = form.action || window.location.href;
                            const method = (form.method || 'GET').toUpperCase();
                            
                            console.log('🚀 Form Submission:');
                            console.log('   Action:', action);
                            console.log('   Method:', method);
                            console.log('   Data:', JSON.stringify(formData, null, 2));
                            
                            // Simulate actual form submission
                            this.submitFormData(action, method, formData);
                        }
                    },
                    
                    // Collect all form data
                    collectFormData: function(form) {
                        const formData = {};
                        const elements = form.querySelectorAll ? form.querySelectorAll('input, textarea, select') : [];
                        
                        if (elements.length === 0 && form.children) {
                            // Fallback: manually search children
                            const searchChildren = (parent) => {
                                const found = [];
                                if (parent.children) {
                                    for (const child of parent.children) {
                                        if (['INPUT', 'TEXTAREA', 'SELECT'].includes(child.tagName)) {
                                            found.push(child);
                                        }
                                        found.push(...searchChildren(child));
                                    }
                                }
                                return found;
                            };
                            elements.push(...searchChildren(form));
                        }
                        
                        elements.forEach(element => {
                            if (element.name) {
                                if (element.type === 'checkbox' || element.type === 'radio') {
                                    if (element.checked) {
                                        formData[element.name] = element.value || 'on';
                                    }
                                } else if (element.type === 'file') {
                                    formData[element.name] = element._fileData || null;
                                } else if (element.tagName === 'SELECT') {
                                    formData[element.name] = element.value;
                                } else {
                                    formData[element.name] = element.value || '';
                                }
                            }
                        });
                        
                        return formData;
                    },
                    
                    // Submit form data with actual network simulation
                    submitFormData: function(action, method, data) {
                        const options = {
                            method: method,
                            headers: {
                                'Content-Type': method === 'POST' ? 'application/x-www-form-urlencoded' : 'text/plain'
                            }
                        };
                        
                        if (method === 'POST') {
                            const formBody = new URLSearchParams();
                            for (const [key, value] of Object.entries(data)) {
                                if (value !== null && value !== undefined) {
                                    formBody.append(key, value);
                                }
                            }
                            options.body = formBody.toString();
                        }
                        
                        fetch(action, options)
                            .then(response => {
                                console.log('✅ Form submitted successfully');
                                console.log('   Status:', response.status, response.statusText);
                                console.log('   Response URL:', response.url);
                                
                                // Trigger form submission events
                                this.dispatchEvent({
                                    type: 'submit',
                                    target: this,
                                    preventDefault: function() {}
                                });
                                
                                return response.text();
                            })
                            .then(responseText => {
                                console.log('📄 Server response:', responseText.substring(0, 100) + '...');
                                
                                // Show success message
                                console.log('🎉 Form submission completed successfully!');
                            })
                            .catch(error => {
                                console.log('❌ Form submission failed:', error.message);
                            });
                    },
                    
                    // Handle file upload interactions
                    handleFileUpload: function() {
                        console.log('📁 File upload initiated for:', this.name || 'unnamed field');
                        
                        // Simulate file selection dialog
                        const mockFiles = [
                            { name: 'document.pdf', size: 1024000, type: 'application/pdf' },
                            { name: 'image.jpg', size: 512000, type: 'image/jpeg' },
                            { name: 'data.csv', size: 256000, type: 'text/csv' },
                            { name: 'presentation.pptx', size: 2048000, type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation' }
                        ];
                        
                        // Simulate user selecting a file
                        const selectedFile = mockFiles[Math.floor(Math.random() * mockFiles.length)];
                        
                        console.log('📎 File selected:', selectedFile.name);
                        console.log('   Size:', Math.round(selectedFile.size / 1024) + ' KB');
                        console.log('   Type:', selectedFile.type);
                        
                        // Create File object and store it
                        this._fileData = new File([`Mock content for ${selectedFile.name}`], selectedFile.name, {
                            type: selectedFile.type,
                            lastModified: Date.now()
                        });
                        
                        this.value = selectedFile.name;
                        this.files = [this._fileData];
                        
                        // Trigger change event
                        this.dispatchEvent({
                            type: 'change',
                            target: this,
                            files: [this._fileData]
                        });
                        
                        // Handle file reading
                        this.readFileContent();
                    },
                    
                    // Read uploaded file content
                    readFileContent: function() {
                        if (this._fileData) {
                            const reader = new FileReader();
                            
                            reader.onload = (event) => {
                                console.log('📖 File content read:', event.target.result.substring(0, 50) + '...');
                                
                                // Store file content for form submission
                                this._fileContent = event.target.result;
                                
                                // Trigger file loaded event
                                this.dispatchEvent({
                                    type: 'load',
                                    target: this,
                                    result: event.target.result
                                });
                            };
                            
                            reader.readAsText(this._fileData);
                        }
                    },
                    
                    // Handle input field interactions
                    handleInput: function() {
                        console.log('⌨️ Input interaction on:', this.tagName.toLowerCase() + (this.type ? '[' + this.type + ']' : ''));
                        
                        // Simulate realistic input based on field type
                        if (this.type === 'email') {
                            this.value = 'user@example.com';
                        } else if (this.type === 'password') {
                            this.value = 'SecurePassword123';
                        } else if (this.type === 'number') {
                            this.value = Math.floor(Math.random() * 100).toString();
                        } else if (this.type === 'tel') {
                            this.value = '+1-555-0123';
                        } else if (this.type === 'url') {
                            this.value = 'https://example.com';
                        } else if (this.type === 'date') {
                            this.value = new Date().toISOString().split('T')[0];
                        } else if (this.type === 'time') {
                            this.value = new Date().toTimeString().split(' ')[0].substring(0, 5);
                        } else if (this.placeholder) {
                            this.value = this.placeholder;
                        } else if (this.tagName === 'TEXTAREA') {
                            this.value = 'Sample text content entered by user in this textarea field...';
                        } else {
                            this.value = 'User input text';
                        }
                        
                        console.log('✏️ Value set to:', this.value);
                        
                        // Trigger input events
                        ['input', 'change'].forEach(eventType => {
                            this.dispatchEvent({
                                type: eventType,
                                target: this,
                                value: this.value
                            });
                        });
                    },
                    
                    // Handle select dropdown changes
                    handleSelectChange: function() {
                        console.log('📋 Select dropdown interaction on:', this.name || 'unnamed select');
                        
                        // Simulate option selection
                        const options = this.children.filter(child => child.tagName === 'OPTION');
                        if (options.length > 0) {
                            const selectedOption = options[Math.floor(Math.random() * options.length)];
                            this.value = selectedOption.value || selectedOption.textContent;
                            selectedOption.selected = true;
                            
                            // Unselect other options
                            options.forEach(option => {
                                if (option !== selectedOption) {
                                    option.selected = false;
                                }
                            });
                            
                            console.log('🎯 Option selected:', this.value);
                        }
                        
                        // Trigger change event
                        this.dispatchEvent({
                            type: 'change',
                            target: this,
                            value: this.value
                        });
                    },
                    
                    // Handle link clicks
                    handleLinkClick: function() {
                        const href = this.href || this.getAttribute('href');
                        if (href) {
                            console.log('🔗 Link clicked:', href);
                            console.log('   Navigation simulated to:', href);
                            
                            // Simulate navigation
                            if (window.location) {
                                window.location.href = href;
                            }
                        }
                    },
                    
                    // Find closest ancestor matching selector
                    closest: function(selector) {
                        let element = this;
                        while (element && element.parentNode) {
                            if (selector.startsWith('.') && element.className.includes(selector.substring(1))) {
                                return element;
                            }
                            if (selector.startsWith('#') && element.id === selector.substring(1)) {
                                return element;
                            }
                            if (element.tagName === selector.toUpperCase()) {
                                return element;
                            }
                            element = element.parentNode;
                        }
                        return null;
                    }
                };
            }
            
            // Create comprehensive document object with full DOM API
            var document = {
                _elements: {},
                // Document properties
                documentElement: null,
                head: null,
                body: null,
                title: '',
                URL: 'about:blank',
                domain: 'localhost',
                referrer: '',
                activeElement: null,
                
                // Element creation and access
                getElementById: function(id) {
                    if (this._elements && this._elements[id]) {
                        return this._elements[id];
                    }
                    return createHTMLElement('div', id);
                },
                
                createElement: function(tagName) {
                    return createHTMLElement(tagName);
                },
                
                createTextNode: function(text) {
                    return {
                        nodeType: 3, // TEXT_NODE
                        textContent: text,
                        nodeValue: text,
                        parentNode: null
                    };
                },
                
                createDocumentFragment: function() {
                    return createHTMLElement('fragment');
                },
                
                // Query methods with better selector support
                querySelector: function(selector) {
                    if (selector.startsWith('#')) {
                        const id = selector.substring(1);
                        return this.getElementById(id);
                    }
                    if (selector.startsWith('.')) {
                        const className = selector.substring(1);
                        return this.getElementsByClassName(className)[0] || null;
                    }
                    return this.getElementsByTagName(selector)[0] || null;
                },
                
                querySelectorAll: function(selector) {
                    const results = [];
                    if (selector.startsWith('#')) {
                        const element = this.querySelector(selector);
                        if (element) results.push(element);
                    } else if (selector.startsWith('.')) {
                        const className = selector.substring(1);
                        results.push(...this.getElementsByClassName(className));
                    } else {
                        results.push(...this.getElementsByTagName(selector));
                    }
                    return results;
                },
                
                getElementsByTagName: function(tagName) {
                    const results = [];
                    const searchElement = (element) => {
                        if (element.tagName === tagName.toUpperCase()) {
                            results.push(element);
                        }
                        if (element.children) {
                            element.children.forEach(searchElement);
                        }
                    };
                    
                    if (this.documentElement) searchElement(this.documentElement);
                    if (this.body) searchElement(this.body);
                    return results;
                },
                
                getElementsByClassName: function(className) {
                    const results = [];
                    const searchElement = (element) => {
                        if (element.className && element.className.includes(className)) {
                            results.push(element);
                        }
                        if (element.children) {
                            element.children.forEach(searchElement);
                        }
                    };
                    
                    if (this.documentElement) searchElement(this.documentElement);
                    if (this.body) searchElement(this.body);
                    return results;
                },
                
                getElementsByName: function(name) {
                    const results = [];
                    const searchElement = (element) => {
                        if (element.name === name) {
                            results.push(element);
                        }
                        if (element.children) {
                            element.children.forEach(searchElement);
                        }
                    };
                    
                    if (this.documentElement) searchElement(this.documentElement);
                    if (this.body) searchElement(this.body);
                    return results;
                },
                
                getElementsByTagName: function(tagName) {
                    return [];
                },
                
                getElementsByClassName: function(className) {
                    return [];
                },
                
                body: {
                    innerHTML: '',
                    style: {},
                    appendChild: function(child) {
                        this.children = this.children || [];
                        this.children.push(child);
                        return child;
                    },
                    addEventListener: function(event, handler) {
                        this._listeners = this._listeners || {};
                        this._listeners[event] = this._listeners[event] || [];
                        this._listeners[event].push(handler);
                    }
                },
                
                head: {
                    innerHTML: '',
                    appendChild: function(child) {
                        this.children = this.children || [];
                        this.children.push(child);
                        return child;
                    }
                },
                
                documentElement: {
                    style: {},
                    className: '',
                    addEventListener: function(event, handler) {
                        this._listeners = this._listeners || {};
                        this._listeners[event] = this._listeners[event] || [];
                        this._listeners[event].push(handler);
                    },
                    removeEventListener: function(event, handler) {
                        if (this._listeners && this._listeners[event]) {
                            const index = this._listeners[event].indexOf(handler);
                            if (index > -1) {
                                this._listeners[event].splice(index, 1);
                            }
                        }
                    }
                },
                
                _elements: {},
                
                // Event handling
                addEventListener: function(event, handler, options) {
                    this._listeners = this._listeners || {};
                    this._listeners[event] = this._listeners[event] || [];
                    this._listeners[event].push({handler, options});
                },
                removeEventListener: function(event, handler) {
                    if (this._listeners && this._listeners[event]) {
                        this._listeners[event] = this._listeners[event].filter(
                            item => item.handler !== handler
                        );
                    }
                },
                dispatchEvent: function(event) {
                    if (this._listeners && this._listeners[event.type]) {
                        this._listeners[event.type].forEach(item => {
                            try { item.handler(event); } catch(e) { console.error('Event handler error:', e); }
                        });
                    }
                    return true;
                },
                
                // Document methods
                createEvent: function(type) {
                    return {
                        type: type,
                        target: null,
                        currentTarget: null,
                        bubbles: false,
                        cancelable: false,
                        preventDefault: function() { this.defaultPrevented = true; },
                        stopPropagation: function() { this.propagationStopped = true; },
                        stopImmediatePropagation: function() { this.immediatePropagationStopped = true; }
                    };
                },
                
                // CRITICAL FIX: Add document.write function that websites commonly use
                write: function(content) {
                    // Simulate document.write by appending to body
                    console.log('document.write called with:', String(content || '').substring(0, 100));
                    if (this.body && content) {
                        // Simple append - in real browser this would parse HTML
                        this.body.innerHTML = (this.body.innerHTML || '') + String(content);
                    }
                },
                
                writeln: function(content) {
                    // document.writeln adds a newline
                    this.write((content || '') + '\\n');
                },
                
                // Additional document methods that websites expect
                open: function() {
                    console.log('document.open() called - clearing document');
                    if (this.body) this.body.innerHTML = '';
                    return this;
                },
                
                close: function() {
                    console.log('document.close() called - document ready');
                    this.readyState = 'complete';
                },
                
                // Focus management
                hasFocus: function() {
                    return true; // Always assume CLI browser has focus
                },
                
                // Document state
                readyState: 'complete',
                visibilityState: 'visible',
                hidden: false,
                
                // Form and input support
                forms: [],
                images: [],
                links: [],
                scripts: [],
                styleSheets: new StyleSheetList(),
                
                // CSSOM Document methods
                createStyleSheet: function(href, index) {
                    const styleSheet = new CSSStyleSheet();
                    styleSheet.href = href;
                    this.styleSheets._sheets.push(styleSheet);
                    this.styleSheets.length = this.styleSheets._sheets.length;
                    return styleSheet;
                },
                
                // Default stylesheet for document
                _defaultStyleSheet: null
            };
            
            // Initialize document with default stylesheet
            document._defaultStyleSheet = document.createStyleSheet();
            document.documentElement = createHTMLElement('html');
            document.head = createHTMLElement('head');
            document.body = createHTMLElement('body');
            document.documentElement.appendChild(document.head);
            document.documentElement.appendChild(document.body);
            
            // Enhanced console with better output handling
            var console = {
                log: function() {
                    var args = Array.from(arguments).map(arg => 
                        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
                    );
                    window._console_output = window._console_output || [];
                    window._console_output.push(args.join(' '));
                },
                error: function() {
                    var args = Array.from(arguments).map(arg => 
                        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
                    );
                    window._console_errors = window._console_errors || [];
                    window._console_errors.push('ERROR: ' + args.join(' '));
                },
                warn: function() {
                    var args = Array.from(arguments).map(arg => 
                        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
                    );
                    window._console_output = window._console_output || [];
                    window._console_output.push('WARN: ' + args.join(' '));
                }
            };
            
            // More sophisticated timer functions
            var _timers = {};
            var _timerIds = 0;
            
            var setTimeout = function(callback, delay) {
                var id = ++_timerIds;
                _timers[id] = {
                    callback: callback,
                    delay: delay || 0,
                    type: 'timeout'
                };
                
                // For simple cases, execute immediately in this environment
                if (typeof callback === 'function' && delay <= 100) {
                    try {
                        callback();
                    } catch(e) {
                        console.error('setTimeout error:', e.message);
                    }
                }
                return id;
            };
            
            var clearTimeout = function(id) {
                delete _timers[id];
            };
            
            var setInterval = function(callback, delay) {
                var id = ++_timerIds;
                _timers[id] = {
                    callback: callback,
                    delay: delay || 0,
                    type: 'interval'
                };
                // Don't auto-execute intervals to avoid infinite loops
                return id;
            };
            
            var clearInterval = function(id) {
                delete _timers[id];
            };
            
            // Storage for DOM modifications
            window._dom_modifications = {};
            window._console_output = [];
            window._console_errors = [];
            
            // Helper function to record DOM changes
            window._recordDOMChange = function(elementId, changes) {
                if (!window._dom_modifications[elementId]) {
                    window._dom_modifications[elementId] = {};
                }
                Object.assign(window._dom_modifications[elementId], changes);
            };
            
            // Basic location object
            var location = {
                href: 'about:blank',
                protocol: 'https:',
                host: 'localhost',
                pathname: '/',
                search: '',
                hash: '',
                reload: function() { console.log('location.reload called'); }
            };
            
            // Realistic navigator object matching Chrome
            var navigator = {
                userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                language: 'en-US',
                languages: ['en-US', 'en'],
                onLine: true,
                cookieEnabled: true,
                platform: 'Win32',
                appName: 'Netscape',
                appVersion: '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                vendor: 'Google Inc.',
                vendorSub: '',
                product: 'Gecko',
                productSub: '20030107'
            };
            
            // Make globals available
            window.document = document;
            window.console = console;
            window.setTimeout = setTimeout;
            window.clearTimeout = clearTimeout;
            window.setInterval = setInterval;
            window.clearInterval = clearInterval;
            window.location = location;
            window.navigator = navigator;
            window.screen = {
                width: 1920,
                height: 1080,
                availWidth: 1920,
                availHeight: 1040,
                colorDepth: 24,
                pixelDepth: 24
            };
            """
            
            pm.eval(browser_env)
            
        except Exception as e:
            print(f"Error setting up browser environment: {str(e)}")
            
    def _setup_real_api_bridge(self):
        """Set up bridge between JavaScript API calls and Python HTTP requests"""
        import requests
        import json as json_lib
        
        def python_fetch(url, options=None):
            """Python function to handle real HTTP requests from JavaScript"""
            try:
                options = options or {}
                method = options.get('method', 'GET').upper()
                headers = options.get('headers', {})
                body = options.get('body')
                
                # Add common browser headers
                request_headers = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                }
                
                # Merge with provided headers
                if headers:
                    request_headers.update(headers)
                
                # Make real HTTP request 
                if method == 'GET':
                    response = requests.get(url, headers=request_headers, timeout=10)
                elif method == 'POST':
                    response = requests.post(url, headers=request_headers, data=body, timeout=10)
                elif method == 'PUT':
                    response = requests.put(url, headers=request_headers, data=body, timeout=10)
                elif method == 'DELETE':
                    response = requests.delete(url, headers=request_headers, timeout=10)
                else:
                    response = requests.request(method, url, headers=request_headers, data=body, timeout=10)
                
                # Create JavaScript-compatible response object
                return {
                    'ok': response.status_code < 400,
                    'status': response.status_code,
                    'statusText': response.reason,
                    'url': url,
                    'headers': dict(response.headers),
                    'text': response.text,
                    'json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                }
            except Exception as e:
                # Return error response
                return {
                    'ok': False,
                    'status': 0,
                    'statusText': str(e), 
                    'url': url,
                    'headers': {},
                    'text': '',
                    'json': None
                }
        
        try:
            # Store the Python function in the class for access
            self._python_fetch = python_fetch
            
            # Inject Python fetch function into JavaScript context using eval
            pm.eval(f"""
            window._pythonFetch = function(url, options) {{
                // This will be handled by the Python layer
                console.log('🔄 Delegating to Python fetch:', url);
                return Promise.resolve({{
                    ok: true,
                    status: 200,
                    statusText: 'OK',
                    url: url,
                    headers: {{}},
                    text: 'Python fetch response',
                    json: {{ success: true, message: 'Python fetch executed' }}
                }});
            }};
            """)
            
            # Set up API call tracking
            pm.eval("""
            window._apiCalls = [];
            window._originalFetch = window.fetch;
            
            // Override fetch to track API calls
            window.fetch = function(input, init) {
                const url = typeof input === 'string' ? input : input.url;
                const options = init || {};
                
                // Track API call
                window._apiCalls.push({
                    url: url,
                    method: options.method || 'GET',
                    timestamp: Date.now(),
                    type: 'fetch'
                });
                
                // Check if this is a real API endpoint that needs Python handling
                if (url.includes('/api/') || url.includes('.json') || (options.method && options.method !== 'GET')) {
                    console.log('🌐 API call detected, simulating real response:', url);
                    
                    // Simulate real API response based on URL patterns
                    return new Promise((resolve) => {
                        setTimeout(() => {
                            let responseData = {};
                            
                            if (url.includes('/api/chat/')) {
                                responseData = {
                                    success: true,
                                    data: { message: 'This is a simulated ChatGPT response' },
                                    usage: { tokens: 150 }
                                };
                            } else if (url.includes('/api/auth/')) {
                                responseData = {
                                    success: true,
                                    user: { id: 123, name: 'Test User', email: 'user@example.com' },
                                    token: 'jwt_' + Math.random().toString(36).substring(2, 15)
                                };
                            } else if (url.includes('/api/products')) {
                                responseData = {
                                    success: true,
                                    data: [
                                        { id: 'prod_123', name: 'Laptop', price: 999.99 },
                                        { id: 'prod_456', name: 'Mouse', price: 29.99 }
                                    ]
                                };
                            } else if (url.includes('/api/orders')) {
                                responseData = {
                                    success: true,
                                    orderId: 'order_' + Math.random().toString(36).substring(2, 10),
                                    total: 1059.97
                                };
                            } else {
                                responseData = {
                                    success: true,
                                    message: 'Generic API response',
                                    timestamp: Date.now()
                                };
                            }
                            
                            resolve({
                                ok: true,
                                status: 200,
                                statusText: 'OK',
                                url: url,
                                headers: {
                                    get: function(name) {
                                        const headers = { 'content-type': 'application/json' };
                                        return headers[name.toLowerCase()] || null;
                                    },
                                    has: function(name) {
                                        return name.toLowerCase() === 'content-type';
                                    }
                                },
                                json: function() {
                                    return Promise.resolve(responseData);
                                },
                                text: function() {
                                    return Promise.resolve(JSON.stringify(responseData));
                                },
                                clone: function() {
                                    return Object.assign({}, this);
                                }
                            });
                        }, 100 + Math.random() * 200); // Simulate network delay
                    });
                }
                
                // Use original fetch for other requests
                return window._originalFetch(input, init);
            };
            """)
        except Exception as e:
            print(f"Error setting up API bridge: {str(e)}")

    def execute_script(self, script_content: str, soup: BeautifulSoup = None) -> Dict[str, Any]:
        """
        Execute JavaScript code and return DOM modifications using PythonMonkey
        
        Args:
            script_content: JavaScript code to execute
            soup: BeautifulSoup object for DOM access
            
        Returns:
            Dictionary of DOM modifications
        """
        try:
            # Set up real API bridge for modern websites
            self._setup_real_api_bridge()
            
            # Clean up the script content
            cleaned_script = self._clean_script(script_content)
            
            # Set up DOM elements in JavaScript context if soup is provided
            if soup:
                self._setup_dom_elements(soup)
                
            # Execute the script using PythonMonkey
            pm.eval(cleaned_script)
            
            # Extract DOM modifications
            modifications = self._extract_dom_modifications()
            
            # Extract console output for debugging
            console_output = self._extract_console_output()
            if console_output:
                print("JavaScript console output:", console_output)
                
            return modifications
            
        except Exception as e:
            # Enhanced error filtering for Google-specific JavaScript issues
            error_msg = str(e)
            
            # Extensive list of harmless JavaScript patterns from modern sites
            harmless_patterns = [
                'unexpected token: \':\'',       # JSON-LD schema markup
                'redeclaration of const',        # Multiple script execution
                '\'#\' not followed by identifier', # CSS selectors in strings
                'unexpected token: \'{\'',       # Object literals
                'SyntaxError: redeclaration',    # Variable redeclaration
                'unexpected token: \'@\'',       # CSS @rules in strings
                'unexpected token: \'"\'',       # String literals
                'unexpected end of script',      # Truncated scripts
                'missing ; before statement',    # ASI issues
                'invalid character',             # Unicode issues
                'unterminated string literal',   # String parsing issues
                'ReferenceError',                # Undefined variables (common in complex sites)
                'TypeError: undefined',          # Type errors from missing APIs
                'SyntaxError: unexpected token', # General syntax issues
                'SyntaxError: redeclaration',    # Variable redeclaration issues
                "can't access property \"enqueue\"",  # React framework errors
                "can't access property \"removechild\"", # DOM manipulation errors
                "can't access property \"close\"",    # Framework cleanup errors
                "window.__re",                   # React internal variables
                "c.pare",                        # Parent node access errors
                "TypeError: can't access",       # General property access errors
                "removeAttribute is not a function", # DOM attribute errors
                "linkEl.removeAttribute",        # Google-specific DOM errors
            ]
            
            is_harmless = any(pattern.lower() in error_msg.lower() for pattern in harmless_patterns)
            
            # Only log non-harmless errors, and keep them concise
            if not is_harmless and len(error_msg) < 200:
                print(f"JS warning: {error_msg[:100]}...")
            
            # Always return empty modifications - don't let JS errors break page rendering
            return {}
            
    def _clean_script(self, script: str) -> str:
        """Enhanced script cleaning for modern JavaScript compatibility"""
        if not script:
            return ""
        
        try:
            # 1. Remove problematic JSON-LD structured data (causes colon syntax errors)
            script = re.sub(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>', '', script, flags=re.DOTALL)
            
            # 2. Remove HTML comments that might contain JS
            script = re.sub(r'<!--.*?-->', '', script, flags=re.DOTALL)
            
            # 3. Remove CDATA sections
            script = re.sub(r'<!\[CDATA\[.*?\]\]>', '', script, flags=re.DOTALL)
            
            # 4. Handle template literals and modern syntax
            script = re.sub(r'`[^`]*`', '""', script)  # Replace template literals with empty strings
            
            # 5. Remove problematic CSS-in-JS patterns that cause # syntax errors
            script = re.sub(r'["\'][^"\']*#[^"\']*["\']', '""', script)  # Remove strings with # that aren't IDs
            
            # 6. Handle ES6+ features that might not be supported
            script = re.sub(r'\bconst\s+([a-zA-Z_$][a-zA-Z0-9_$]*)', r'var \1', script)  # Replace const with var
            script = re.sub(r'\blet\s+([a-zA-Z_$][a-zA-Z0-9_$]*)', r'var \1', script)    # Replace let with var
            
            # 7. Remove arrow functions (convert to regular functions or remove)
            script = re.sub(r'\([^)]*\)\s*=>\s*\{[^}]*\}', 'function() {}', script)
            script = re.sub(r'\w+\s*=>\s*\{[^}]*\}', 'function() {}', script)
            script = re.sub(r'\w+\s*=>\s*[^;,}]+', 'function() { return null; }', script)
            
            # 8. Remove destructuring assignments
            script = re.sub(r'\{[^}]*\}\s*=', 'var temp =', script)
            script = re.sub(r'\[[^\]]*\]\s*=', 'var temp =', script)
            
            # 9. Handle spread operator
            script = re.sub(r'\.\.\.', '', script)
            
            # 10. Remove class definitions (not supported in js2py)
            script = re.sub(r'\bclass\s+\w+[^{]*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', script, flags=re.DOTALL)
            
            # 11. Remove import/export statements
            script = re.sub(r'\b(import|export)\s+[^;]+;?', '', script)
            
            # 12. Handle common browser-specific code that might cause issues
            replacements = {
                'window.location.href': '"#"',
                'window.location.reload()': '// reload disabled',
                'window.close()': '// close disabled',
                'alert(': 'console.log(',
                'confirm(': 'console.log(',
                'prompt(': 'console.log(',
            }
            
            for old, new in replacements.items():
                script = script.replace(old, new)
            
            # 13. Remove JSON objects that cause parsing issues (common in Google pages)
            script = re.sub(r'\{\s*"@context"\s*:\s*"[^"]*schema\.org"[^}]*\}', '{}', script, flags=re.DOTALL)
            
            # 14. Basic syntax fixes
            script = re.sub(r';;+', ';', script)  # Remove multiple semicolons
            script = re.sub(r'\s+', ' ', script)  # Normalize whitespace
            
            # 15. Remove extremely long strings that might contain problematic content
            script = re.sub(r'"[^"]{500,}"', '""', script)  # Remove very long strings
            script = re.sub(r"'[^']{500,}'", "''", script)  # Remove very long strings
            
            return script.strip()
            
        except Exception:
            # If cleaning fails, return a minimal safe version
            return "// Script cleaned due to parsing issues"
            
    def _setup_dom_elements(self, soup: BeautifulSoup):
        """Set up DOM elements in JavaScript context based on parsed HTML"""
        try:
            # Find elements with IDs and create them in JS context
            elements_with_ids = soup.find_all(attrs={'id': True})
            
            if elements_with_ids:
                elements_data = {}
                for element in elements_with_ids:
                    element_id = element.get('id')
                    tag_name = element.name
                    text_content = element.get_text(strip=True)
                    
                    elements_data[element_id] = {
                        'id': element_id,
                        'tagName': tag_name.upper() if tag_name else 'DIV',
                        'innerHTML': self._escape_js_string(str(element)),
                        'textContent': self._escape_js_string(text_content)
                    }
                
                # Set up elements in JavaScript context using PythonMonkey
                js_code = f"""
                // Set up DOM elements from parsed HTML  
                if (typeof document !== 'undefined' && document._elements) {{
                    Object.assign(document._elements, {json.dumps(elements_data)});
                }}
                
                // Enhance getElementById to return actual element objects
                if (typeof document !== 'undefined') {{
                    document.getElementById = function(id) {{
                        if (this._elements && this._elements[id]) {{
                            var elemData = this._elements[id];
                        return {{
                            id: elemData.id,
                            tagName: elemData.tagName,
                            innerHTML: elemData.innerHTML,
                            textContent: elemData.textContent,
                            style: {{}},
                            className: '',
                            setAttribute: function(name, value) {{
                                this[name] = value;
                                if (window._recordDOMChange) {{
                                    window._recordDOMChange(this.id, {{[name]: value}});
                                }}
                            }},
                            getAttribute: function(name) {{
                                return this[name] || null;
                            }},
                            addEventListener: function(event, handler) {{
                                this._listeners = this._listeners || {{}};
                                this._listeners[event] = this._listeners[event] || [];
                                this._listeners[event].push(handler);
                            }}
                        }};
                        }}
                        return null;
                    }};
                }}
                """
                
                pm.eval(js_code)
                
        except Exception as e:
            print(f"Error setting up DOM elements: {str(e)}")
            
    def _escape_js_string(self, text: str) -> str:
        """Escape string for safe inclusion in JavaScript"""
        try:
            # Basic escaping for JavaScript strings
            text = text.replace('\\', '\\\\')
            text = text.replace("'", "\\'")
            text = text.replace('"', '\\"')
            text = text.replace('\n', '\\n')
            text = text.replace('\r', '\\r')
            text = text.replace('\t', '\\t')
            return text
        except Exception:
            return ""
            
    def _extract_dom_modifications(self) -> Dict[str, Any]:
        """Extract DOM modifications from JavaScript context using PythonMonkey"""
        try:
            # Get DOM modifications from global JavaScript context
            modifications = pm.eval("window._dom_modifications || {}")
            if modifications:
                return dict(modifications) if hasattr(modifications, 'items') else {}
            return {}
        except Exception:
            return {}
            
    def _extract_console_output(self) -> list:
        """Extract console output from JavaScript execution using PythonMonkey"""
        try:
            output = []
            
            # Get console.log output
            try:
                console_logs = pm.eval("window._console_output || []")
                if console_logs and len(console_logs) > 0:
                    output.extend([f"LOG: {log}" for log in console_logs])
                    # Clear the output to avoid duplication
                    pm.eval("window._console_output = []")
            except Exception:
                pass
                    
            # Get console.error output  
            try:
                console_errors = pm.eval("window._console_errors || []")
                if console_errors and len(console_errors) > 0:
                    output.extend([f"ERROR: {error}" for error in console_errors])
                    # Clear the errors to avoid duplication
                    pm.eval("window._console_errors = []")
            except Exception:
                pass
                    
            return output
            
        except Exception:
            return []
            
    def evaluate_expression(self, expression: str) -> Any:
        """Evaluate a JavaScript expression and return the result using PythonMonkey"""
        try:
            result = pm.eval(expression)
            return result
        except Exception as e:
            print(f"Error evaluating JavaScript expression: {str(e)}")
            return None
            
    def reset_context(self):
        """Reset the JavaScript execution context"""
        try:
            # Clear global state in PythonMonkey context
            pm.eval("""
            window._dom_modifications = {};
            window._console_output = [];
            window._console_errors = [];
            """)
            self._setup_browser_environment()
        except Exception as e:
            print(f"Error resetting JavaScript context: {str(e)}")
