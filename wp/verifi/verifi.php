<?php
/*
Plugin Name: Verifi
Description: Permet la vérification sur les listes électorales
Version: 1.0
Author: Salomé Cheysson
License: GPL3
*/

namespace LFI\WPPlugins\Verifi;

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

class Plugin
{

    /**
     * Constructor.
     */
    public function __construct()
    {
        add_action('init', [$this, 'admin_init']);
        add_action('elementor_pro/init', [$this, 'register_elementor_addons']);
        add_shortcode('verifi', [$this, 'shortcode_handler']);
    }

    public function admin_init()
    {
        require_once dirname(__FILE__) . '/admin.php';

        new Admin();
    }

    public function register_elementor_addons()
    {
        require_once dirname(__FILE__) . '/verifi-handler.php';

        $elementor_verifi_action = new VerifiAction();
        \ElementorPro\Plugin::instance()
            ->modules_manager->get_modules('forms')
            ->add_form_action($elementor_verifi_action->get_name(), $elementor_verifi_action);
    }

    public function shortcode_handler( $atts, $content, $tag ) {
        require_once dirname(__FILE__) . '/verifi-shortcode.php';
        return verifi_shortcode( $atts );
    }

}

new Plugin();
