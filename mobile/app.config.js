// Expo app configuration with environment variable support
// This file is used instead of app.json to allow dynamic configuration

export default {
  expo: {
    name: "mobile",
    slug: "mobile",
    version: "1.0.0",
    orientation: "portrait",
    icon: "./assets/icon.png",
    userInterfaceStyle: "light",
    newArchEnabled: true,
    splash: {
      image: "./assets/splash-icon.png",
      resizeMode: "contain",
      backgroundColor: "#ffffff"
    },
    ios: {
      supportsTablet: true
    },
    android: {
      adaptiveIcon: {
        foregroundImage: "./assets/adaptive-icon.png",
        backgroundColor: "#ffffff"
      },
      edgeToEdgeEnabled: true,
      predictiveBackGestureEnabled: false
    },
    web: {
      favicon: "./assets/favicon.png"
    },
    // Extra configuration for environment variables
    // Access via Constants.expoConfig.extra
    extra: {
      apiBaseUrl: process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8001/api/v1',
      appName: process.env.EXPO_PUBLIC_APP_NAME || 'FitCoach',
      appVersion: process.env.EXPO_PUBLIC_APP_VERSION || '1.0.0',
      // Add other environment variables as needed
    }
  }
};
