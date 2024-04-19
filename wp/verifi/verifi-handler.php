<?php

namespace LFI\WPPlugins\Verifi;


use ElementorPro\Modules\Forms\Classes\Action_Base;

if (!defined('ABSPATH')) {
  exit; // Exit if accessed directly
}

class VerifiAction extends Action_Base
{
  const FIELDS = array(
    "code_com" => "code_com",
    "date_naissance" => 'date_of_birth',
    "nom" => 'last_name',
    "prenoms" => 'first_name',
    "sexe" => 'gender',
  );

  public function get_name()
  {
    return 'verifi';
  }

  public function get_label()
  {
    return "Vérifier sur les listes électorales";
  }

  public function run($record, $ajax_handler)
  {
    $settings = $record->get('form_settings');
    $raw_fields = $record->get('fields');

    $data = array();
    foreach( self::FIELDS as $key => $name ) {
      $data[$key] = $raw_fields[$name]['value'];
    }

    if (empty($data['nom'])) {
      $ajax_handler->add_error("last_name", "Votre nom de famille est obligatoire.");
    }

    if (empty($data['prenoms'])) {
      $ajax_handler->add_error("first_name", "Indiquez bien tous vos prénoms, séparés par des espaces.");
    }

    if (empty($data['sexe'])) {
      $ajax_handler->add_error("gender", "Indiquez votre sexe à l'état civil.");
    }

    if (empty($data['date_naissance'])) {
      $ajax_handler->add_error("date_of_birth", "Indiquez votre date de naissance.");
    } else if ( preg_match('/^\d{4}-\d{2}-\d{2}$/', $data['date_naissance'] ) ) {
      $data['date_naissance'] = implode(
        '/',
        array_reverse( explode('-', $data['date_naissance'] ) )
      );
    }

    if ( empty($data["code_com"]) ) {
      $ajax_handler->add_error("code_com", "Sélectionnez la commune dans laquelle vous pensez être inscrits.");
    } else if ( !preg_match('/^\d[\dAB]\d\d\d$/', $data["code_com"]) ) {
      $ajax_handler->add_error("code_com", "Format du code commune incorrect.");
    }

    if (count($ajax_handler->errors) > 0) {
      return;
    }

    $data["election"] = $settings['verifi_election'];

    $options = get_option('lfi_verifi');

    $base_url = $options['api_url'];
    $url = add_query_arg( $data, $base_url );

    $response = wp_remote_get($url, [
      'headers' => [
        'X-Wordpress-Client' => $_SERVER['REMOTE_ADDR']
      ],
    ]);

    if (is_wp_error($response) || $response['response']['code'] != 200) {
      $ajax_handler->add_error_message($response["body"]);
      return;
    }

    $result = json_decode( $response["body"], true );

    switch( $result['status'] ) {
      case 'invalide':
        foreach ($result['errors'] as $key => $error ) {
          $ajax_handler->add_error( self::FIELDS[$key], $error);
        }
        break;

      case 'commune manquante':
        $ajax_handler->add_error_message(<<<EOM
Malheureusement, la préfecture refuse pour le moment de nous transmettre les listes
électorales pour votre commune. Nous mettrons à jour l'application dès que nous
pourrons la récupérer.
EOM
        );
        break;

      case 'pas inscrit':
        $ajax_handler->add_error_message(<<<EOM
Nous ne parvenons pas à trouver vos informations dans la liste électorale de cette commune.
<strong>Vous n'êtes potentiellement pas inscrit.</strong><br>"
Assurez-vous d'avoir correctement saisi vos informations personnelles. Vous devez fournir
tous les prénoms qui figurent sur vos papiers pour pouvoir trouver votre inscription.<br>
EOM
        );
        break;

      case 'inscrit':
        $bureau = $result['electeur']['bureau'];
        $numero = $result['electeur']['num_electeur'];
        $ajax_handler->add_success_message(<<<EOM
Nous avons pu trouver votre inscription sur les listes électorales de cette commune.<br>
Vous voterez au bureau n° $bureau, avec le numéro d'électeur·ice $numero.
EOM

        );
        break;

      default:
        $ajax_handler->add_error_message("Une erreur imprévue s'est produite.");
    }
  }

  public function register_settings_section($widget)
  {
    $widget->start_controls_section('section_verifi', [
      'label' => 'Vérifier sur les listes électorales',
      'condition' => [
        'submit_actions' => $this->get_name(),
      ],
    ]);

    $widget->add_control(
      'verifi_election',
      [
        'label' => "Type de scrutin",
        'type' => \Elementor\Controls_Manager::SELECT,
        'description' => 'Certains électeurs supplémentaires peuvent voter aux scrutins européens et municipaux.',
        'options' => [
          "municipales" => 'Élections municipales',
          'europeennes' => "Élections européennes",
          'autre' => "Autres scrutins",
        ],
        'default' => 'autre'
      ]
    );

    $widget->end_controls_section();
  }

  public function on_export($element)
  {
    unset($element['verifi_election']);
    return $element;
  }
}
