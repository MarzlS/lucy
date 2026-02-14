#!/usr/bin/env node
/**
 * Lucy's Aura - LED control script
 * Controls a Neopixel LED on GPIO 18 to express emotions and moods.
 * 
 * Usage:
 *   node aura.js <command> [options]
 * 
 * Commands:
 *   shine <color>              - Set LED to a solid color
 *   pulse <color> [duration]   - Pulse the LED (duration: 0.5-2.0 seconds)
 *   disco [duration]           - Party mode! Random colors blinking
 *   off                        - Turn off the LED
 *   emotion <name>             - Show a predefined emotion
 * 
 * Colors: red, green, blue, yellow, orange, purple, pink, cyan, white, or hex (#FF0000)
 * Emotions: happy, sad, excited, calm, thinking, love, angry, surprised
 */

import ws281x from 'rpi-ws281x-native';
import colornames from 'colornames';

const GPIO_PIN = 18;
const NUM_LEDS = 1;

// Initialize the LED
const channel = ws281x(NUM_LEDS, { gpioPin: GPIO_PIN });
const colors = channel.array;

// Emotion color mappings
const EMOTIONS = {
    happy: { color: '#FFD700', mode: 'pulse' },      // Gold
    sad: { color: '#4169E1', mode: 'shine' },        // Royal Blue
    excited: { color: 'random', mode: 'disco' },     // Disco!
    calm: { color: '#98FB98', mode: 'pulse' },       // Pale Green
    thinking: { color: '#9370DB', mode: 'pulse' },   // Medium Purple
    love: { color: '#FF1493', mode: 'pulse' },       // Deep Pink
    angry: { color: '#FF0000', mode: 'shine' },      // Red
    surprised: { color: '#FFFF00', mode: 'pulse' },  // Yellow
    neutral: { color: '#FFFFFF', mode: 'shine' },    // White (dim)
};

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function normalizeColor(color) {
    if (!color) return 0x000000;
    
    let c = color.toLowerCase();
    
    if (c === 'off') return 0x000000;
    if (c === 'on') return 0xFFFFFF;
    if (c === 'random') {
        return Math.floor(Math.random() * 0xFFFFFF);
    }
    
    // Handle hex colors
    if (c.startsWith('#')) {
        c = c.slice(1);
    }
    if (c.startsWith('0x')) {
        c = c.slice(2);
    }
    
    // Check if it's a valid hex
    if (/^[0-9A-Fa-f]{6}$/.test(c)) {
        return parseInt(c, 16);
    }
    
    // Try colornames package
    const hex = colornames(c);
    if (hex) {
        return parseInt(hex.slice(1), 16);
    }
    
    console.error(`Unknown color: ${color}`);
    return 0xFFFFFF;
}

function shine(color) {
    const c = normalizeColor(color);
    colors[0] = c;
    ws281x.render();
    console.log(`LED shining: ${color} (0x${c.toString(16).padStart(6, '0')})`);
}

async function pulse(color, duration = 1.0) {
    const steps = 20;
    const c = normalizeColor(color);
    const r = (c >> 16) & 0xFF;
    const g = (c >> 8) & 0xFF;
    const b = c & 0xFF;
    
    const stepDelay = (duration * 1000) / steps;
    
    // Fade in
    for (let i = 0; i <= steps / 2; i++) {
        const brightness = i / (steps / 2);
        const pr = Math.round(r * brightness);
        const pg = Math.round(g * brightness);
        const pb = Math.round(b * brightness);
        colors[0] = (pr << 16) | (pg << 8) | pb;
        ws281x.render();
        await sleep(stepDelay);
    }
    
    // Fade out
    for (let i = steps / 2; i >= 0; i--) {
        const brightness = i / (steps / 2);
        const pr = Math.round(r * brightness);
        const pg = Math.round(g * brightness);
        const pb = Math.round(b * brightness);
        colors[0] = (pr << 16) | (pg << 8) | pb;
        ws281x.render();
        await sleep(stepDelay);
    }
    
    console.log(`LED pulsed: ${color}`);
}

async function disco(duration = 5) {
    const endTime = Date.now() + (duration * 1000);
    console.log(`Disco mode for ${duration} seconds!`);
    
    while (Date.now() < endTime) {
        colors[0] = Math.floor(Math.random() * 0xFFFFFF);
        ws281x.render();
        await sleep(100);
    }
    
    // Turn off after disco
    colors[0] = 0;
    ws281x.render();
    console.log('Disco finished!');
}

async function showEmotion(emotionName) {
    const emotion = EMOTIONS[emotionName.toLowerCase()];
    if (!emotion) {
        console.error(`Unknown emotion: ${emotionName}`);
        console.log(`Available emotions: ${Object.keys(EMOTIONS).join(', ')}`);
        process.exit(1);
    }
    
    console.log(`Showing emotion: ${emotionName}`);
    
    switch (emotion.mode) {
        case 'shine':
            shine(emotion.color);
            break;
        case 'pulse':
            await pulse(emotion.color, 1.5);
            await pulse(emotion.color, 1.5);
            break;
        case 'disco':
            await disco(3);
            break;
    }
}

function off() {
    colors[0] = 0;
    ws281x.render();
    console.log('LED off');
}

function cleanup() {
    ws281x.reset();
    process.exit(0);
}

// Handle cleanup on exit
process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);

// Main
async function main() {
    const args = process.argv.slice(2);
    const command = args[0];
    
    if (!command) {
        console.log('Usage: node aura.js <command> [options]');
        console.log('Commands: shine, pulse, disco, off, emotion');
        console.log('Example: node aura.js shine red');
        console.log('Example: node aura.js emotion happy');
        console.log('Example: node aura.js disco 5');
        process.exit(1);
    }
    
    try {
        switch (command.toLowerCase()) {
            case 'shine':
                shine(args[1] || 'white');
                break;
            case 'pulse':
                await pulse(args[1] || 'white', parseFloat(args[2]) || 1.0);
                break;
            case 'disco':
                await disco(parseFloat(args[1]) || 5);
                break;
            case 'off':
                off();
                break;
            case 'emotion':
                await showEmotion(args[1] || 'neutral');
                break;
            default:
                // Maybe it's a color directly
                shine(command);
        }
    } catch (err) {
        console.error('Error:', err.message);
        process.exit(1);
    }
    
    // Keep running for shine, exit for others
    if (command === 'shine' || (command === 'emotion' && EMOTIONS[args[1]?.toLowerCase()]?.mode === 'shine')) {
        // Keep the process alive to maintain LED state
        // Exit after 100ms to let the LED stay on
        await sleep(100);
    }
    
    process.exit(0);
}

main();
