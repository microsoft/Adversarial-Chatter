import * as CryptoJS from 'crypto-js';

const crypto = require('crypto');

export class PasswordValidator{
    validatePassword(password: string) {
    if (password.length < 8) return { isValid: false, message: 'Password must be at least 8 characters long.' };
    if (!/[A-Z]/.test(password)) return { isValid: false, message: 'Password must contain at least one uppercase letter.' };
    if (!/[a-z]/.test(password)) return { isValid: false, message: 'Password must contain at least one lowercase letter.' };
    if (!/[0-9]/.test(password)) return { isValid: false, message: 'Password must contain at least one digit.' };
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) return { isValid: false, message: 'Password must contain at least one special character.' };
    return { isValid: true, message: 'Password is valid.' };
    }

    hashPassword(password: string) {
        // Create a new sha256 hash object
        const sha256 = new TextEncoder().encode(password);
        return crypto.subtle.digest('SHA-256', sha256).then((hashBuffer: ArrayBuffer) => {
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
            return hashHex;
        });
    }
}



