(function () {
    var COLOR_KEY = 'mw-color-scheme';
    var MODE_KEY = 'mw-theme-mode';
    var BACKGROUND_KEY = 'mw-theme-background';
    var BACKGROUND_KIND_KEY = 'mw-theme-background-kind';
    var BACKGROUND_SOURCE_KEY = 'mw-theme-background-source';
    var BACKGROUND_MODE_KEY = 'mw-theme-background-mode';
    var DEFAULT_COLOR = '#0f766e';
    var DEFAULT_MODE = 'auto';
    var THEME_CLASSES = ['mdui-theme-light', 'mdui-theme-dark', 'mdui-theme-auto'];
    var MEMORY_STORE = {};

    function getRoot() {
        return document.documentElement;
    }

    function normalizeMode(mode) {
        if (mode === 'light' || mode === 'dark' || mode === 'auto') {
            return mode;
        }
        return DEFAULT_MODE;
    }

    function safeGet(key) {
        if (Object.prototype.hasOwnProperty.call(MEMORY_STORE, key)) {
            return MEMORY_STORE[key];
        }
        try {
            var value = window.localStorage.getItem(key);
            if (value !== null) {
                return value;
            }
        } catch (error) {
        }
        return null;
    }

    function safeSet(key, value) {
        try {
            window.localStorage.setItem(key, value);
        } catch (error) {}
        MEMORY_STORE[key] = value;
    }

    function safeRemove(key) {
        try {
            window.localStorage.removeItem(key);
        } catch (error) {}
        MEMORY_STORE[key] = null;
    }

    function escapeCssUrl(value) {
        return String(value).replace(/\\/g, '\\\\').replace(/"/g, '\\"');
    }

    function hexToRgbTriplet(color) {
        if (!color) {
            return null;
        }

        var value = String(color).trim().replace(/^#/, '');
        if (value.length === 3) {
            value = value.split('').map(function (ch) {
                return ch + ch;
            }).join('');
        }

        if (value.length !== 6) {
            return null;
        }

        var red = parseInt(value.slice(0, 2), 16);
        var green = parseInt(value.slice(2, 4), 16);
        var blue = parseInt(value.slice(4, 6), 16);
        if (isNaN(red) || isNaN(green) || isNaN(blue)) {
            return null;
        }

        return red + ', ' + green + ', ' + blue;
    }

    function normalizeBackgroundValue(value) {
        if (!value) {
            return '';
        }

        var trimmed = String(value).trim();
        if (!trimmed) {
            return '';
        }

        if (trimmed.toLowerCase() === 'none') {
            return '';
        }

        if (/^(url|linear-gradient|radial-gradient|repeating-linear-gradient|repeating-radial-gradient)\(/i.test(trimmed)) {
            return trimmed;
        }

        return 'url("' + escapeCssUrl(trimmed) + '")';
    }

    function applyColorScheme(color) {
        if (!color) {
            return;
        }

        if (window.mdui && typeof window.mdui.setColorScheme === 'function') {
            window.mdui.setColorScheme(color);
        }

        getRoot().style.setProperty('--mw-theme-primary', color);
        var rgb = hexToRgbTriplet(color);
        if (rgb) {
            getRoot().style.setProperty('--mw-theme-primary-rgb', rgb);
        }
    }

    function resetColorScheme() {
        if (window.mdui && typeof window.mdui.removeColorScheme === 'function') {
            window.mdui.removeColorScheme();
        }

        getRoot().style.removeProperty('--mw-theme-primary');
        getRoot().style.removeProperty('--mw-theme-primary-rgb');
        applyColorScheme(DEFAULT_COLOR);
    }

    function applyMode(mode) {
        var nextMode = normalizeMode(mode);
        var root = getRoot();

        if (window.mdui && typeof window.mdui.setTheme === 'function') {
            window.mdui.setTheme(nextMode, root);
            return;
        }

        for (var i = 0; i < THEME_CLASSES.length; i++) {
            root.classList.remove(THEME_CLASSES[i]);
        }
        root.classList.add('mdui-theme-' + nextMode);
    }

    function clearBackgroundValue() {
        safeRemove(BACKGROUND_KEY);
        safeRemove(BACKGROUND_KIND_KEY);
        safeRemove(BACKGROUND_SOURCE_KEY);
        getRoot().style.removeProperty('--mw-app-background-image');
    }

    function applyBackgroundMode(mode) {
        var nextMode = mode === 'plain' ? 'plain' : 'default';
        if (nextMode === 'plain') {
            getRoot().style.setProperty('--mw-app-background-overlay', 'none');
        } else {
            getRoot().style.removeProperty('--mw-app-background-overlay');
        }
    }

    function getBackgroundMode() {
        return safeGet(BACKGROUND_MODE_KEY) || 'default';
    }

    function setBackgroundMode(mode) {
        var nextMode = mode === 'plain' ? 'plain' : 'default';
        safeSet(BACKGROUND_MODE_KEY, nextMode);
        applyBackgroundMode(nextMode);
    }

    function applyBackgroundValue(background) {
        var value = normalizeBackgroundValue(background);
        if (!value) {
            clearBackgroundValue();
            return;
        }

        safeSet(BACKGROUND_KEY, value);
        getRoot().style.setProperty('--mw-app-background-image', value);
    }

    function setBackground(background, meta) {
        var value = normalizeBackgroundValue(background);
        if (!value) {
            clearBackgroundValue();
            return;
        }

        safeSet(BACKGROUND_KEY, value);
        safeSet(BACKGROUND_MODE_KEY, getBackgroundMode());
        safeSet(BACKGROUND_KIND_KEY, meta && meta.kind ? meta.kind : 'custom');
        if (meta && meta.source) {
            safeSet(BACKGROUND_SOURCE_KEY, meta.source);
        } else {
            safeRemove(BACKGROUND_SOURCE_KEY);
        }
        getRoot().style.setProperty('--mw-app-background-image', value);
    }

    function setBackgroundUrl(url) {
        if (!url) {
            return;
        }

        setBackground(url, {
            kind: 'url',
            source: url
        });
    }

    function setBackgroundFile(file) {
        return new Promise(function (resolve, reject) {
            if (!file) {
                resolve(null);
                return;
            }

            var reader = new FileReader();
            reader.onload = function () {
                var result = reader.result || '';
                setBackground(result, {
                    kind: 'upload',
                    source: file.name || 'upload'
                });
                resolve({
                    value: result,
                    kind: 'upload',
                    source: file.name || 'upload'
                });
            };
            reader.onerror = function () {
                reject(reader.error || new Error('failed to read background file'));
            };
            reader.readAsDataURL(file);
        });
    }

    function clearBackground() {
        setBackgroundMode('plain');
        clearBackgroundValue();
    }

    function setDefaultBackground() {
        setBackgroundMode('default');
        clearBackgroundValue();
    }

    function getMode() {
        return normalizeMode(safeGet(MODE_KEY));
    }

    function setMode(mode) {
        var nextMode = normalizeMode(mode);
        safeSet(MODE_KEY, nextMode);
        applyMode(nextMode);
    }

    function getBackgroundInfo() {
        return {
            value: safeGet(BACKGROUND_KEY) || '',
            kind: safeGet(BACKGROUND_KIND_KEY) || 'default',
            source: safeGet(BACKGROUND_SOURCE_KEY) || '',
            mode: getBackgroundMode()
        };
    }

    function initTheme() {
        var storedColor = safeGet(COLOR_KEY);
        var storedMode = normalizeMode(safeGet(MODE_KEY));
        var storedBackground = safeGet(BACKGROUND_KEY);
        var storedBackgroundMode = getBackgroundMode();

        applyMode(storedMode);
        applyBackgroundMode(storedBackgroundMode);

        if (storedColor) {
            applyColorScheme(storedColor);
        } else {
            applyColorScheme(DEFAULT_COLOR);
        }

        if (storedBackground) {
            getRoot().style.setProperty('--mw-app-background-image', storedBackground);
            if (!safeGet(BACKGROUND_KIND_KEY)) {
                safeSet(BACKGROUND_KIND_KEY, 'custom');
            }
        }
    }

    window.MWTheme = {
        init: initTheme,
        applyColor: function (color) {
            if (!color) {
                return;
            }
            safeSet(COLOR_KEY, color);
            applyColorScheme(color);
        },
        reset: function () {
            safeRemove(COLOR_KEY);
            resetColorScheme();
        },
        getStoredColor: function () {
            return safeGet(COLOR_KEY);
        },
        getColor: function () {
            return safeGet(COLOR_KEY) || DEFAULT_COLOR;
        },
        setMode: setMode,
        getMode: getMode,
        setBackground: setBackground,
        setBackgroundUrl: setBackgroundUrl,
        setBackgroundFile: setBackgroundFile,
        setDefaultBackground: setDefaultBackground,
        clearBackground: clearBackground,
        applyBackground: applyBackgroundValue,
        getBackground: function () {
            return safeGet(BACKGROUND_KEY);
        },
        getBackgroundInfo: getBackgroundInfo,
        getBackgroundMode: getBackgroundMode,
        setBackgroundMode: setBackgroundMode,
        getBackgroundKind: function () {
            return safeGet(BACKGROUND_KIND_KEY) || 'default';
        },
        getBackgroundSource: function () {
            return safeGet(BACKGROUND_SOURCE_KEY) || '';
        }
    };
})();
