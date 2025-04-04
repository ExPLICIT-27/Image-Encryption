#include "image_encryptor.h"
#include <iostream>
#include <vector>
#include <fstream>
#include <string>

using namespace std;

struct Pixel
{
    unsigned char r, g, b;
};

struct CatMapParams
{
    int p, q;
    int iterations;
};

class Image
{
private:
    vector<Pixel> pixels;
    int width, height;

public:
    Image(int w, int h) : width(w), height(h)
    {
        pixels.resize(width * height);
    }

    int getWidth() const { return width; }
    int getHeight() const { return height; }

    int index(int i, int j) const
    {
        return i * width + j;
    }

    bool readPPM(const string &filename)
    {
        ifstream file(filename, ios::binary);
        if (!file)
        {
            cerr << "Error: Cannot open file " << filename << endl;
            return false;
        }

        string format;
        file >> format;
        if (format != "P6")
        {
            cerr << "Error: Unsupported format (not P6 PPM)" << endl;
            return false;
        }

        file >> width >> height;
        int maxVal;
        file >> maxVal;
        file.ignore(1);

        pixels.resize(width * height);
        file.read(reinterpret_cast<char *>(&pixels[0]), width * height * sizeof(Pixel));

        return true;
    }

    bool writePPM(const string &filename)
    {
        ofstream file(filename, ios::binary);
        if (!file)
        {
            cerr << "Error: Cannot write to file " << filename << endl;
            return false;
        }

        file << "P6\n"
             << width << " " << height << "\n255\n";
        file.write(reinterpret_cast<const char *>(&pixels[0]), width * height * sizeof(Pixel));

        return true;
    }

    void applyCatMap(const CatMapParams &params)
    {
        vector<Pixel> temp = pixels;
        for (int i = 0; i < height; i++)
        {
            for (int j = 0; j < width; j++)
            {
                int newX = (j + i) % width;
                int newY = (j + 2 * i) % height;
                pixels[index(newY, newX)] = temp[index(i, j)];
            }
        }
    }

    void applyInverseCatMap(const CatMapParams &params)
    {
        if (width != height)
        {
            cerr << "Error: Inverse Arnold transformation requires a square image." << endl;
            return;
        }

        int N = width;
        vector<Pixel> temp = pixels;
        for (int newRow = 0; newRow < N; newRow++)
        {
            for (int newCol = 0; newCol < N; newCol++)
            {
                int origRow = ((newRow - newCol) % N + N) % N;
                int origCol = ((2 * newCol - newRow) % N + N) % N;
                pixels[index(origRow, origCol)] = temp[index(newRow, newCol)];
            }
        }
    }

    void scrambleImage(const CatMapParams &params)
    {
        if (width != height)
        {
            cerr << "Error: Scrambling is optimized for square images." << endl;
            return;
        }

        for (int i = 0; i < params.iterations; i++)
        {
            applyCatMap(params);
        }
    }

    void unscrambleImage(const CatMapParams &params)
    {
        if (width != height)
        {
            cerr << "Error: Unscrambling requires a square image." << endl;
            return;
        }

        for (int i = 0; i < params.iterations; i++)
        {
            applyInverseCatMap(params);
        }
    }
};

void scramble(const char *inputPath, const char *outputPath, int iterations)
{
    Image img(0, 0);
    if (!img.readPPM(inputPath))
    {
        return;
    }

    CatMapParams params = {1, 1, iterations};
    img.scrambleImage(params);
    img.writePPM(outputPath);
}

void unscramble(const char *inputPath, const char *outputPath, int iterations)
{
    Image img(0, 0);
    if (!img.readPPM(inputPath))
    {
        return;
    }

    CatMapParams params = {1, 1, iterations};
    img.unscrambleImage(params);
    img.writePPM(outputPath);
}
