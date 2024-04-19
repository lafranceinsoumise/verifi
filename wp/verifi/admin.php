<?php

namespace LFI\WPPlugins\Verifi;

if ( ! defined( 'ABSPATH' ) ) {
    exit; // Exit if accessed directly
}

class Admin
{
    public function __construct()
    {
        // When initialized
        add_action('admin_init', [$this, 'settings_init']);

        // When menu load
        add_action('admin_menu', [$this, 'add_admin_menu']);
    }

    public function add_admin_menu()
    {
        add_submenu_page(
            'lfi',
            'LFI | Verifi',
            'Verifi',
            'manage_options',
            'lfi_verifi',
            [$this, 'options_page']
        );
    }

    public function options_page()
    {
        ?>
        <h1>Paramètres de Verifi</h1>
        <form action="options.php" method="post">
            <?php
            settings_fields('lfi_verifi');
            do_settings_sections('lfi_verifi');
            submit_button("Enregistrer"); ?>
        </form>
        <?php

    }

    public function settings_init()
    {
        register_setting(
            'lfi_verifi',
            'lfi_verifi',
            array( 'type' => 'array', 'default' => array( 'api_url' => '' ) )
        );

        add_settings_section(
            'verifi_api_section',
            'Paramètres de l\'API',
            [$this, 'verifi_api_section_callback'],
            'lfi_verifi'
        );

        add_settings_field(
            'api_url',
            'URL de l\'API',
            [$this, 'verifi_url_render'],
            'lfi_verifi',
            'verifi_api_section'
        );

    }

    public function verifi_api_section_callback()
    {
        ?>
        <p>Les paramètres pour se connecter à l'API verifi.</p>
        <?php
    }


    public function verifi_url_render()
    {
        $options = get_option('lfi_verifi'); ?>

        <input type="text"
               name="lfi_verifi[api_url]"
               value="<?= isset($options['api_url']) ? esc_attr($options['api_url']) : ''; ?>">
        <?php
    }
}
