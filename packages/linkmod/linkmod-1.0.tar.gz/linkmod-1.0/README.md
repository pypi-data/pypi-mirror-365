# LinkMod: The Ultimate Command-Line URL Tool



**LinkMod** is a powerful and flexible command-line tool that enhances your URL management workflow. It offers two primary functionalities:

1.  **Bitly URL Shortening**: Quickly shorten long URLs using the Bitly API.
2.  **Custom Link Naming**: Create memorable, custom-named links in the format `custom-name@your-link.com`.

When you provide a long URL and a custom name, LinkMod will first shorten the URL with Bitly (if an API key is available) and then create a custom link with the shortened URL.

## Features

-   **Seamless Bitly Integration**: Shorten URLs with a single command.
-   **Secure API Key Storage**: Your Bitly API key is stored securely in your system's native credential manager using the `keyring` library.
-   **Cross-Platform**: Works on Windows, macOS, and Linux.
-   **User-Friendly Prompts**: The tool guides you through setting up your Bitly API key for the first time.
-   **Flexible Usage**: Use either the URL shortening, the custom link naming, or both combined.

## Installation

You can install LinkMod using `pip`:

```bash
pip install .
```

This will install the package and all its dependencies (`requests` and `keyring`).

## Usage

LinkMod's functionality changes based on the number of arguments you provide.

### 1. Shorten a URL with Bitly

To shorten a long URL, simply provide it as a single argument:

```bash
linkMod {long_url}
```

**Example:**

```bash
linkMod https://www.github.com/Rishi-Bhati/linkmod
```

**Output:**

```
Short link: https://bit.ly/xxxxxxx
```

### 2. Create a Custom Link (with optional Bitly shortening)

To create a custom-named link, provide the original URL and your desired custom name:

```bash
linkMod {long_url} {custom_name}
```

**Example:**

```bash
linkMod https://www.github.com/Rishi-Bhati/linkmod my-repo
```

**Output:**

```
Checking for Bitly API key...
Bitly API key found. Shortening link...
Link shortened successfully.
my-repo@bit.ly/xxxxxxx
```

If no Bitly API key is found, the tool will use the original link:

```
Checking for Bitly API key...
Bitly API key not found. Using original link.
my-repo@www.github.com/Rishi-Bhati/linkmod
```

### Setting Up Your Bitly API Key

The first time you use a feature that requires a Bitly API key, the tool will prompt you to add one:

```
Bitly API key not found. Would you like to add one? (y/n):
```

If you select `y`, you will be prompted to enter your API key. It will then be securely stored for all future uses.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue on the [GitHub repository](https://github.com/Rishi-Bhati/linkmod.git).

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
