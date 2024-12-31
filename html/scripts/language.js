// language.js

let translations = {};

document.addEventListener("DOMContentLoaded", async () => {
    // 0) Récupération des traductions
    try {
        const response = await fetch('../translations.json');
        translations = await response.json();
    } catch (error) {
        console.error('Error loading translations:', error);
    }

    // 1) Récupération de la langue préférée
    const currentLanguage = localStorage.getItem('preferred_language') || 'fr';

    // 2) Initialisation du select#language-selector
    const languageSelector = document.getElementById("language-selector");

    // Vider le select, si vous aviez déjà mis des <option> en dur dans le HTML :
    languageSelector.innerHTML = "";

    // Parcourir les clés de translations (ex: "fr", "en", etc.) pour créer les <option>
    for (let langCode in translations) {
        const option = document.createElement("option");
        option.value = langCode;
        option.textContent = translations[langCode]["language"];

        // Si c’est la langue actuelle, on la sélectionne
        if (langCode === currentLanguage) {
          option.selected = true;
        }
        languageSelector.appendChild(option);
    }

    // 3) Appliquer la langue préférée
    applyLanguage(currentLanguage);

    // 4) Gérer le changement de langue lors d’une nouvelle sélection
    languageSelector.addEventListener("change", (e) => {
        const newLang = e.target.value;
        // Sauvegarder la nouvelle langue dans le localStorage
        localStorage.setItem("preferred_language", newLang);
        // Appliquer la nouvelle langue
        applyLanguage(newLang);
    });
});

/**
 * Fonction qui applique la langue `lang` à tous les éléments textuels de la page
 * en se basant sur l'objet `translations`.
 */
function applyLanguage(lang) {
    const dictionary = translations[lang];

    if (!dictionary) {
        console.warn(`La langue "${lang}" n'est pas définie dans les translations.`);
        return;
    }

    // Pour chaque clé dans la traduction de la langue, on applique la valeur
    for (let key in dictionary) {
        const text = dictionary[key];

        // Gestion des placeholders : on adopte une convention "id.placeholder"
        // ex: "objective.placeholder"
        if (key.includes(".placeholder")) {
          // key = "objective.placeholder" => on sépare
          const [baseId, attr] = key.split("."); // ["objective", "placeholder"]
          const element = document.getElementById(baseId);
          if (element) {
            element.placeholder = text;
          }
        } else {
          // Sinon, on modifie textContent (ou innerHTML si besoin)
          const element = document.getElementById(key);
          if (element) {
            element.textContent = text;
          }
        }
    }
}
