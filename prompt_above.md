I'm using LaTeX with custom macros to make a songbook. Here is what a song file looks like:

```
\begin{song}

\SongTitle{Happy Birthday}{traditional}

\begin{headerbox}
\RaiseBoxWithAccents
\beatsperchord4 \quad
\textit{Strum:} $\Down\Miss\AccentDown\Up\Miss\Up\AccentDown\Up$
\end{headerbox}

\begin{hchordbox}
\ukechord{C}
\ukechord{D}
\ukechord{G}
\end{hchordbox}

\Large

\bigskip

Happy \ch{G}birthday to \ch{D}you \par
Happy \ch{D}birthday to \ch{G}you \par
Happy \ch{G}birthday, dear \ch{C}(insert name) \par
Happy \ch{G}birthday \ch{D}to \ch{G}you \par

\end{song}
```

Please help me write the song file. Below is a text with chords for a song. The chord notation is on every other line above the text. Wrap each chord in `\ch{...}` and insert it in the text just before the word it is written above - the exact position
matters. For example,

```
    C                    F
She asked me, "Son, when I grow old,
     Am           G
Will you buy me a house of gold?
```
becomes
```
She \ch{C}asked me, "Son, when \ch{F}I grow old, \par
Will \ch{Am}you buy me a \ch{G}house of gold? \par
```


Moreover:
* Add `\par` at the end of every line. Add a space before if the line is not empty.
* On every line, make the first letter of the song text a capital
* Add `\bigskip` after every verse and chorus
* Wrap each chorus in `\begin{chorusbox}{\Chorus}` and `\end{chorusbox}`

Here is the text:

```
<claude seems best>
```
