import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import * as Localization from 'expo-localization';

// Import translations
import en from './locales/en.json';
import ru from './locales/ru.json';
import cz from './locales/cz.json';

const resources = {
  en: { translation: en },
  ru: { translation: ru },
  cz: { translation: cz },
};

i18n
  .use(initReactI18next)
  .init({
    compatibilityJSON: 'v3',
    resources,
    lng: Localization.locale.split('-')[0], // Get device language (e.g., 'en' from 'en-US')
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
