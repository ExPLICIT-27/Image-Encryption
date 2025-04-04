#ifndef IMAGE_ENCRYPTOR_H
#define IMAGE_ENCRYPTOR_H

#ifdef __cplusplus
extern "C"
{
#endif

    void scramble(const char *inputPath, const char *outputPath, int iterations);
    void unscramble(const char *inputPath, const char *outputPath, int iterations);

#ifdef __cplusplus
}
#endif

#endif // IMAGE_ENCRYPTOR_H
