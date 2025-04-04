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

    // void applyCatMap(const CatMapParams &params)
    // {
    //     vector<Pixel> temp = pixels;
    //     for (int i = 0; i < height; i++)
    //     {
    //         for (int j = 0; j < width; j++)
    //         {
    //             int newX = (j + i) % width;
    //             int newY = (j + 2 * i) % height;
    //             pixels[index(newY, newX)] = temp[index(i, j)];
    //         }
    //     }
    // }
    void multiplyMatrix(int a[2][2], int b[2][2], int N, int result[2][2])
    {
        int temp[2][2];
        temp[0][0] = (a[0][0] * b[0][0] + a[0][1] * b[1][0]) % N;
        temp[0][1] = (a[0][0] * b[0][1] + a[0][1] * b[1][1]) % N;
        temp[1][0] = (a[1][0] * b[0][0] + a[1][1] * b[1][0]) % N;
        temp[1][1] = (a[1][0] * b[0][1] + a[1][1] * b[1][1]) % N;

        result[0][0] = temp[0][0];
        result[0][1] = temp[0][1];
        result[1][0] = temp[1][0];
        result[1][1] = temp[1][1];
    }

    void powerMatrix(int base[2][2], int exp, int N, int result[2][2])
    {
        // Start with identity matrix
        result[0][0] = 1;
        result[0][1] = 0;
        result[1][0] = 0;
        result[1][1] = 1;

        while (exp > 0)
        {
            if (exp % 2 == 1)
            {
                multiplyMatrix(result, base, N, result);
            }
            multiplyMatrix(base, base, N, base);
            exp /= 2;
        }
    }
    void applyCatMap(const CatMapParams &params)
    {
        int N = width;
        if (N != height)
        {
            cerr << "Error: Arnold Cat Map requires a square image.\n";
            return;
        }

        int T[2][2] = {{1, 1}, {1, 2}};
        int Tn[2][2];
        powerMatrix(T, params.iterations, N, Tn);

        vector<Pixel> temp = pixels;

        for (int i = 0; i < N; i++)
        {
            for (int j = 0; j < N; j++)
            {
                int x_new = (Tn[0][0] * j + Tn[0][1] * i) % N;
                int y_new = (Tn[1][0] * j + Tn[1][1] * i) % N;
                pixels[index(y_new, x_new)] = temp[index(i, j)];
            }
        }
    }

    // void applyInverseCatMap(const CatMapParams &params)
    // {
    //     if (width != height)
    //     {
    //         cerr << "Error: Inverse Arnold transformation requires a square image." << endl;
    //         return;
    //     }

    //     int N = width;
    //     vector<Pixel> temp = pixels;
    //     for (int newRow = 0; newRow < N; newRow++)
    //     {
    //         for (int newCol = 0; newCol < N; newCol++)
    //         {
    //             int origRow = ((newRow - newCol) % N + N) % N;
    //             int origCol = ((2 * newCol - newRow) % N + N) % N;
    //             pixels[index(origRow, origCol)] = temp[index(newRow, newCol)];
    //         }
    //     }
    // }
    void modMatrix(int mat[2][2], int N)
    {
        for (int i = 0; i < 2; i++)
            for (int j = 0; j < 2; j++)
                mat[i][j] = (mat[i][j] % N + N) % N;
    }
    void applyInverseCatMap(const CatMapParams &params)
    {
        int N = width;
        if (N != height)
        {
            cerr << "Error: Inverse Arnold transformation requires a square image." << endl;
            return;
        }

        // Inverse of Arnold matrix mod N
        int Tinv[2][2] = {{2, -1}, {-1, 1}};
        modMatrix(Tinv, N);

        // Raise to the power of iterations
        int TinvN[2][2];
        powerMatrix(Tinv, params.iterations, N, TinvN);

        vector<Pixel> temp = pixels;

        for (int i = 0; i < N; i++)
        {
            for (int j = 0; j < N; j++)
            {
                int x_new = (TinvN[0][0] * j + TinvN[0][1] * i) % N;
                int y_new = (TinvN[1][0] * j + TinvN[1][1] * i) % N;

                // Ensure non-negative coordinates
                x_new = (x_new + N) % N;
                y_new = (y_new + N) % N;

                pixels[index(y_new, x_new)] = temp[index(i, j)];
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
