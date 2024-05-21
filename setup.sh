mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"prakashash18@gmail.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml

curl -fsSL https://ollama.com/install.sh | sh
