<script lang="ts">
    import { Block } from "@gradio/atoms";

  /**
   * @prop {object | undefined} value - The payload received from the backend.
   * It is an object with 'js' and 'css' string properties. It will be
   * `undefined` on initial mount and will be updated later by a Gradio event.
   */
  export let value;
  
  /**
   * This is a Svelte reactive statement. The code inside this block
   * will re-run whenever any of its dependent variables (in this case, 'value')
   * changes. This is the key to making the component work with demo.load().
   */
  $: {
    // This check is crucial because the block runs on mount when `value` is undefined.
    if (value && (value.js || value.css)) {
      const head = document.head;

      // Use a unique ID for the style element to prevent duplicate injections
      // if the component were to re-render with the same data.
      const styleId = 'gradio-custom-head-styles';
      if (value.css && !document.getElementById(styleId)) {
        const styleElement = document.createElement('style');
        styleElement.id = styleId;
        styleElement.innerHTML = value.css;
        head.appendChild(styleElement);
      }

      // Use a unique ID for the script element for the same reason.
      const scriptId = 'gradio-custom-head-script';
      if (value.js && !document.getElementById(scriptId)) {
        const scriptElement = document.createElement('script');
        scriptElement.id = scriptId;
        scriptElement.innerHTML = value.js;
        head.appendChild(scriptElement);
      }
    }
  }
</script>
<div class="hidden-wrapper">
    <Block style="border-width: 0 !important; padding: 0 !important; margin: 0 !important;">      
    </Block>
</div>
<style>
   .hidden-wrapper {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        position: absolute; 
    }
</style>
