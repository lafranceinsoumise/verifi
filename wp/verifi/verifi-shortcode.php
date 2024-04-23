<?php
namespace LFI\WPPlugins\Verifi;


function verifi_shortcode( $atts ) {
    $FIELDS = array(
        "code_com", "date_naissance", "nom", "prenoms", "sexe"
    );

    $atts = shortcode_atts(
        ['election' => 'autre'],
        $atts
    );

    $election = $atts['election'];
    $options = get_option('lfi_verifi');

    $empty_value = false;

    $data = [];

    foreach($FIELDS as $field) {
        if ( !isset( $_GET[$field] ) || empty( $_GET[$field]) ) {
            $empty_value = true;
            break;
        }
        $data[$field] = $_GET[$field];
    }

    if ( $empty_value ) {
        return "Veuillez remplir le formulaire ci-dessous pour vérifier votre inscription dans les listes électorales.";
    }

    $data['election'] = $election;

    if ( preg_match('/^\d{4}-\d{2}-\d{2}$/', $data['date_naissance'] ) ) {
        $data['date_naissance'] = implode(
            '/',
            array_reverse( explode('-', $data['date_naissance'] ) )
        );
    }

    $base_url = $options['api_url'];
    $url = add_query_arg( $data, $base_url );

    $response = wp_remote_get($url, [
        'headers' => [
            'X-Wordpress-Client' => $_SERVER['REMOTE_ADDR']
        ],
    ]);

    if (is_wp_error($response) || $response['response']['code'] != 200) {
        return "Une erreur inconnue est survenue.";
    }

    $result = json_decode( $response['body'], true );

    switch( $result['status'] ) {
      case 'commune manquante':
        return <<<EOM
<div class="commune-manquante">
<p>
Malheureusement, <strong>la préfecture refuse pour le moment de nous transmettre les listes
électorales pour votre commune</strong>. Nous mettrons à jour l'application dès que nous
pourrons la récupérer.
</p>
<p>
En attendant, <a href="https://www.service-public.fr/particuliers/vosdroits/R51788">vous pouvez faire usage du service proposé par l'État</a>,
mais il vous faudra vous créer un compte spécifique.
</p>
<a class="action" href="https://www.service-public.fr/particuliers/vosdroits/R51788">Accéder au service officiel pour vérifier son inscription</a>
</div>
EOM;

      case 'pas inscrit':
        return <<<EOM
<div class="pas-inscrit">
<p>
Nous ne parvenons pas à trouver vos informations dans la liste électorale de cette commune.
<strong>Vous n'êtes potentiellement pas inscrit·e.</strong><br>
</p>
<p>
Assurez-vous d'avoir correctement saisi vos informations personnelles. Vous devez fournir
tous les prénoms qui figurent sur vos papiers pour pouvoir trouver votre inscription.
</p>
<p>
S'il s'avère que vous n'êtes pas inscrits, <strong>vous avez jusqu'au 1er mai pour <a href="https://www.service-public.fr/particuliers/vosdroits/R16396">vous inscrire sur internet</a> et jusqu'au 3 mai pour vous inscrire en mairie.</strong>
</p>
<a class="action" href="https://www.service-public.fr/particuliers/vosdroits/R16396">Je m'inscris sur les listes électorales en ligne</a>
</div>
EOM;

    case 'inscrit':
        $bureau = $result['electeur']['bureau'];
        $numero = $result['electeur']['num_electeur'];
        return <<<EOM
<div class="inscrit">
<p>
Nous avons pu trouver votre inscription sur les listes électorales de cette commune. <strong>Vous êtes correctement inscrit·e sur les listes électorales.</strong>
</p>
<p>
Le jour du scrutin, vous voterez au bureau n°$bureau, avec le numéro d'électeur·ice $numero.
</p>
</div>
EOM;

    default:
        return "Une erreur inconnue est survenue.";
    }
}
