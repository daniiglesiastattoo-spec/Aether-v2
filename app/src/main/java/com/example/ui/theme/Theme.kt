package com.example.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val DarkColorScheme = darkColorScheme(
    primary = AccentCyan,
    onPrimary = BackgroundDark,
    background = BackgroundDark,
    onBackground = TextPrincipal,
    surface = DarkCardBg,
    onSurface = TextPrincipal,
    error = StatusRed,
    onError = TextPrincipal
)

@Composable
fun MyApplicationTheme(
    darkTheme: Boolean = true, // Force Sci-Fi Dark Theme by default
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        typography = Typography,
        content = content
    )
}
