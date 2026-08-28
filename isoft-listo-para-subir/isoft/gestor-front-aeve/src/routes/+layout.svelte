<script>
    import '../app.css';
    import iconLogo from "../assets/Logo.png";


    let { children } = $props();
</script>

<svelte:head>
    <link rel="icon" href={iconLogo} />
</svelte:head>

{@render children()}
