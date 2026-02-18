<template>
    <div class="container">
        {{ schema }}
    </div>
</template>
<script>
    import axios from 'axios';
    export default {
        data() {
            return {
                schema: {},
            }
        },

        methods: {
            getSchema() {
                const path = 'http://localhost:5000/project_schema';
                axios.get(path)
                    .then((res) => {
                        this.schema = res.data.schema;
                    })
                    .catch((error) => {
                        console.error(error);
                    })
            }
        },

        // Lifecycle hooks
        created() {
            this.getSchema();
        },
    };
</script>