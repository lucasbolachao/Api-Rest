import Keycloak from 'keycloak-js';

const keycloakConfig = {
  url: 'http://localhost:8080',
  realm: 'meu_realm', // Troque pelo seu realm
  clientId: 'meu-frontend' // Troque pelo clientId que criou no Keycloak
};

const keycloak = new Keycloak(keycloakConfig);

export default keycloak;