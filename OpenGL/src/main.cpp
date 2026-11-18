// trabalho final de computacao grafica, modelo hierarquico
// robo humanoide que fica parado, anda e corre
// feito com opengl, glfw, glad e glm

#include <glad/glad.h>
#include <GLFW/glfw3.h>

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

// medidas do robo em metros, as pernas tambem entram na cinematica inversa
constexpr float PI            = 3.14159265358979f;
constexpr float THIGH_LEN     = 0.45f;  // quadril ate joelho
constexpr float SHIN_LEN      = 0.45f;  // joelho ate tornozelo
constexpr float ANKLE_H       = 0.08f;  // tornozelo ate a sola
constexpr float HIP_HALF      = 0.12f;  // metade da distancia entre os quadris
constexpr float UPPER_ARM_LEN = 0.30f;  // ombro ate cotovelo
constexpr float FOREARM_LEN   = 0.27f;  // cotovelo ate punho

// cores
const glm::vec3 COL_METAL  (0.80f, 0.83f, 0.87f);
const glm::vec3 COL_DARK   (0.22f, 0.24f, 0.28f);
const glm::vec3 COL_ACCENT (0.95f, 0.48f, 0.12f);
const glm::vec3 COL_FACE   (0.06f, 0.07f, 0.09f);
const glm::vec3 COL_GLOW   (0.30f, 0.95f, 1.00f);
const glm::vec3 COL_SKY    (0.62f, 0.74f, 0.86f);
const glm::vec3 LIGHT_DIR  = glm::normalize(glm::vec3(0.45f, 1.0f, 0.35f));  // direcao da luz

// shaders

const char* VERTEX_SHADER = R"(
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;

uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProj;
uniform mat3 uNormalMat;

out vec3 vWorldPos;
out vec3 vNormal;

void main() {
    vec4 world = uModel * vec4(aPos, 1.0);
    vWorldPos  = world.xyz;
    vNormal    = uNormalMat * aNormal;
    gl_Position = uProj * uView * world;
}
)";

// umode 0 iluminado, 1 emissivo, 2 chao xadrez, 3 sombra
const char* FRAGMENT_SHADER = R"(
#version 330 core
in vec3 vWorldPos;
in vec3 vNormal;
out vec4 FragColor;

uniform int   uMode;
uniform vec3  uColor;
uniform vec3  uLightDir;
uniform vec3  uCamPos;
uniform vec3  uFogColor;
uniform float uAlpha;

// xadrez filtrado pra nao serrilhar de longe
float checker(vec2 p) {
    vec2 w = max(fwidth(p), vec2(1e-4));
    vec2 i = 2.0 * (abs(fract((p - 0.5 * w) * 0.5) - 0.5) -
                    abs(fract((p + 0.5 * w) * 0.5) - 0.5)) / w;
    return 0.5 - 0.5 * i.x * i.y;
}

void main() {
    float dist = length(uCamPos - vWorldPos);
    float fog  = 1.0 - exp(-pow(dist * 0.028, 2.0));

    if (uMode == 3) {                       // sombra
        FragColor = vec4(0.0, 0.0, 0.0, uAlpha * (1.0 - fog));
        return;
    }

    vec3 base = uColor;
    if (uMode == 2)
        base = mix(vec3(0.86, 0.87, 0.89), vec3(0.58, 0.61, 0.66), checker(vWorldPos.xz));

    vec3 color;
    if (uMode == 1) {
        color = base;                       // emissivo nao recebe luz
    } else {
        vec3 N = normalize(vNormal);
        vec3 L = normalize(uLightDir);
        vec3 V = normalize(uCamPos - vWorldPos);
        vec3 H = normalize(L + V);
        float diff = max(dot(N, L), 0.0);
        float spec = (uMode == 2) ? 0.0 : pow(max(dot(N, H), 0.0), 48.0) * 0.45 * step(0.0, dot(N, L));
        vec3 ambient = mix(vec3(0.32, 0.30, 0.27), vec3(0.50, 0.58, 0.72), 0.5 + 0.5 * N.y) * 0.55;
        color = base * (ambient + diff * vec3(1.0, 0.96, 0.88) * 0.85) + vec3(spec);
    }
    FragColor = vec4(mix(color, uFogColor, fog), 1.0);
}
)";

struct ShaderProgram {
    GLuint id = 0;
    GLint uModel = -1, uView = -1, uProj = -1, uNormalMat = -1;
    GLint uMode = -1, uColor = -1, uLightDir = -1, uCamPos = -1, uFogColor = -1, uAlpha = -1;
};

GLuint compileShader(GLenum type, const char* source) {
    GLuint shader = glCreateShader(type);
    glShaderSource(shader, 1, &source, nullptr);
    glCompileShader(shader);
    GLint ok = 0;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        char log[1024];
        glGetShaderInfoLog(shader, sizeof(log), nullptr, log);
        std::cerr << "Erro ao compilar shader:\n" << log << '\n';
    }
    return shader;
}

ShaderProgram createProgram(const char* vsSource, const char* fsSource) {
    GLuint vs = compileShader(GL_VERTEX_SHADER, vsSource);
    GLuint fs = compileShader(GL_FRAGMENT_SHADER, fsSource);
    ShaderProgram p;
    p.id = glCreateProgram();
    glAttachShader(p.id, vs);
    glAttachShader(p.id, fs);
    glLinkProgram(p.id);
    GLint ok = 0;
    glGetProgramiv(p.id, GL_LINK_STATUS, &ok);
    if (!ok) {
        char log[1024];
        glGetProgramInfoLog(p.id, sizeof(log), nullptr, log);
        std::cerr << "Erro ao linkar programa:\n" << log << '\n';
    }
    glDeleteShader(vs);
    glDeleteShader(fs);

    p.uModel     = glGetUniformLocation(p.id, "uModel");
    p.uView      = glGetUniformLocation(p.id, "uView");
    p.uProj      = glGetUniformLocation(p.id, "uProj");
    p.uNormalMat = glGetUniformLocation(p.id, "uNormalMat");
    p.uMode      = glGetUniformLocation(p.id, "uMode");
    p.uColor     = glGetUniformLocation(p.id, "uColor");
    p.uLightDir  = glGetUniformLocation(p.id, "uLightDir");
    p.uCamPos    = glGetUniformLocation(p.id, "uCamPos");
    p.uFogColor  = glGetUniformLocation(p.id, "uFogColor");
    p.uAlpha     = glGetUniformLocation(p.id, "uAlpha");
    return p;
}

// malhas

struct Mesh {
    GLuint vao = 0, vbo = 0, ebo = 0;
    GLsizei count = 0;
};

// cada vertice tem posicao e normal intercaladas
Mesh uploadMesh(const std::vector<float>& vertices, const std::vector<unsigned>& indices) {
    Mesh m;
    glGenVertexArrays(1, &m.vao);
    glGenBuffers(1, &m.vbo);
    glGenBuffers(1, &m.ebo);

    glBindVertexArray(m.vao);
    glBindBuffer(GL_ARRAY_BUFFER, m.vbo);
    glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(float), vertices.data(), GL_STATIC_DRAW);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, m.ebo);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned), indices.data(), GL_STATIC_DRAW);

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), reinterpret_cast<void*>(0));
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), reinterpret_cast<void*>(3 * sizeof(float)));
    glEnableVertexAttribArray(1);
    glBindVertexArray(0);

    m.count = static_cast<GLsizei>(indices.size());
    return m;
}

void drawMesh(const Mesh& m) {
    glBindVertexArray(m.vao);
    glDrawElements(GL_TRIANGLES, m.count, GL_UNSIGNED_INT, nullptr);
}

void destroyMesh(Mesh& m) {
    glDeleteVertexArrays(1, &m.vao);
    glDeleteBuffers(1, &m.vbo);
    glDeleteBuffers(1, &m.ebo);
    m = Mesh{};
}

// cubo de lado 1 centrado na origem
Mesh createCube() {
    std::vector<float> v;
    std::vector<unsigned> idx;
    const glm::vec3 normals[6] = {{1, 0, 0}, {-1, 0, 0}, {0, 1, 0}, {0, -1, 0}, {0, 0, 1}, {0, 0, -1}};
    for (const glm::vec3& n : normals) {
        glm::vec3 u = (std::abs(n.y) > 0.5f) ? glm::vec3(1, 0, 0) : glm::vec3(0, 1, 0);
        glm::vec3 w = glm::cross(n, u);
        glm::vec3 c = n * 0.5f;
        glm::vec3 corners[4] = {c - 0.5f * u - 0.5f * w, c + 0.5f * u - 0.5f * w,
                                c + 0.5f * u + 0.5f * w, c - 0.5f * u + 0.5f * w};
        unsigned base = static_cast<unsigned>(v.size() / 6);
        for (const glm::vec3& p : corners) v.insert(v.end(), {p.x, p.y, p.z, n.x, n.y, n.z});
        idx.insert(idx.end(), {base, base + 1, base + 2, base, base + 2, base + 3});
    }
    return uploadMesh(v, idx);
}

// esfera de diametro 1 centrada na origem
Mesh createSphere(int stacks, int slices) {
    std::vector<float> v;
    std::vector<unsigned> idx;
    for (int i = 0; i <= stacks; ++i) {
        float phi = PI * static_cast<float>(i) / static_cast<float>(stacks);
        for (int j = 0; j <= slices; ++j) {
            float theta = 2.0f * PI * static_cast<float>(j) / static_cast<float>(slices);
            glm::vec3 n(std::sin(phi) * std::cos(theta), std::cos(phi), std::sin(phi) * std::sin(theta));
            v.insert(v.end(), {0.5f * n.x, 0.5f * n.y, 0.5f * n.z, n.x, n.y, n.z});
        }
    }
    for (int i = 0; i < stacks; ++i) {
        for (int j = 0; j < slices; ++j) {
            unsigned a = static_cast<unsigned>(i * (slices + 1) + j);
            unsigned b = a + static_cast<unsigned>(slices + 1);
            idx.insert(idx.end(), {a, b, a + 1, a + 1, b, b + 1});
        }
    }
    return uploadMesh(v, idx);
}

// plano 1x1 no chao com a normal pra cima
Mesh createPlane() {
    std::vector<float> v = {
        -0.5f, 0.0f, -0.5f, 0, 1, 0,
         0.5f, 0.0f, -0.5f, 0, 1, 0,
         0.5f, 0.0f,  0.5f, 0, 1, 0,
        -0.5f, 0.0f,  0.5f, 0, 1, 0,
    };
    return uploadMesh(v, {0, 2, 1, 0, 3, 2});
}

// modelo hierarquico

enum class Shape { Cube, Sphere };

// peca presa numa articulacao, a escala dela nao passa pros filhos
struct Part {
    Shape shape;
    glm::vec3 offset;
    glm::vec3 size;
    glm::vec3 color;
    bool emissive;
};

struct Node {
    std::string name;
    glm::vec3 jointOffset{0.0f};  // posicao da articulacao em relacao ao pai
    glm::vec3 rotation{0.0f};     // angulos em graus, mudados pela animacao
    std::vector<Part> parts;
    std::vector<std::unique_ptr<Node>> children;
    glm::mat4 world{1.0f};        // matriz de mundo do no

    Node* addChild(const std::string& childName, const glm::vec3& offset) {
        children.push_back(std::make_unique<Node>());
        Node* c = children.back().get();
        c->name = childName;
        c->jointOffset = offset;
        return c;
    }

    Node* part(Shape s, const glm::vec3& off, const glm::vec3& size, const glm::vec3& col, bool emissive = false) {
        parts.push_back(Part{s, off, size, col, emissive});
        return this;
    }
};

// percorre a arvore acumulando as transformacoes
// a matriz do filho e a do pai vezes a translacao vezes as rotacoes em z, y e x
void updateTransforms(Node* node, const glm::mat4& parent) {
    glm::mat4 m = glm::translate(parent, node->jointOffset);
    m = glm::rotate(m, glm::radians(node->rotation.z), glm::vec3(0, 0, 1));
    m = glm::rotate(m, glm::radians(node->rotation.y), glm::vec3(0, 1, 0));
    m = glm::rotate(m, glm::radians(node->rotation.x), glm::vec3(1, 0, 0));
    node->world = m;
    for (auto& child : node->children) updateTransforms(child.get(), m);
}

enum Side { ESQ = 0, DIR = 1 };  // esquerda fica no x positivo, o robo olha pro z positivo

struct Robot {
    std::unique_ptr<Node> root;   // a raiz e o quadril
    Node* pelvis = nullptr;
    Node* torso = nullptr;
    Node* neck = nullptr;
    Node* head = nullptr;
    Node* upperArm[2] = {};
    Node* forearm[2] = {};
    Node* hand[2] = {};
    Node* thigh[2] = {};
    Node* shin[2] = {};
    Node* foot[2] = {};
};

// do quadril saem o tronco e as pernas
// do tronco saem o pescoco com a cabeca e os dois bracos
Robot buildRobot() {
    using S = Shape;
    Robot r;
    r.root = std::make_unique<Node>();
    r.pelvis = r.root.get();
    r.pelvis->name = "quadril";
    r.pelvis->part(S::Cube, {0, 0.05f, 0}, {0.34f, 0.16f, 0.22f}, COL_DARK);

    // tronco
    r.torso = r.pelvis->addChild("tronco", {0, 0.13f, 0});
    r.torso->part(S::Cube, {0, 0.07f, 0},      {0.24f, 0.14f, 0.16f}, COL_DARK)     // cintura
           ->part(S::Cube, {0, 0.32f, 0},      {0.46f, 0.36f, 0.26f}, COL_METAL)    // peito
           ->part(S::Cube, {0, 0.34f, 0.135f}, {0.26f, 0.16f, 0.02f}, COL_ACCENT)   // placa do peito
           ->part(S::Cube, {0, 0.34f, 0.147f}, {0.08f, 0.08f, 0.02f}, COL_GLOW, true)
           ->part(S::Cube, {0, 0.33f, -0.16f}, {0.30f, 0.24f, 0.08f}, COL_DARK);    // mochila

    // pescoco e cabeca
    r.neck = r.torso->addChild("pescoco", {0, 0.50f, 0});
    r.neck->part(S::Cube, {0, 0.04f, 0}, {0.10f, 0.08f, 0.10f}, COL_DARK);

    r.head = r.neck->addChild("cabeca", {0, 0.08f, 0});
    r.head->part(S::Cube,   {0, 0.13f, 0},          {0.30f, 0.26f, 0.27f},    COL_METAL)
          ->part(S::Cube,   {0, 0.14f, 0.136f},     {0.24f, 0.12f, 0.02f},    COL_FACE)   // visor
          ->part(S::Cube,   {0.06f, 0.145f, 0.148f},  {0.06f, 0.035f, 0.012f}, COL_GLOW, true)
          ->part(S::Cube,   {-0.06f, 0.145f, 0.148f}, {0.06f, 0.035f, 0.012f}, COL_GLOW, true)
          ->part(S::Cube,   {0.165f, 0.13f, 0},     {0.03f, 0.08f, 0.08f},    COL_ACCENT) // orelhas
          ->part(S::Cube,   {-0.165f, 0.13f, 0},    {0.03f, 0.08f, 0.08f},    COL_ACCENT)
          ->part(S::Cube,   {0, 0.32f, 0},          {0.018f, 0.12f, 0.018f},  COL_DARK)   // antena
          ->part(S::Sphere, {0, 0.39f, 0},          glm::vec3(0.05f),         COL_ACCENT, true);

    for (int side = ESQ; side <= DIR; ++side) {
        const float sx = (side == ESQ) ? 1.0f : -1.0f;
        const std::string tag = (side == ESQ) ? "_E" : "_D";

        // braco, ombro cotovelo e punho
        Node* arm = r.torso->addChild("braco" + tag, {sx * 0.30f, 0.44f, 0});
        arm->part(S::Sphere, {0, 0, 0},      glm::vec3(0.15f),      COL_ACCENT)
           ->part(S::Cube,   {0, -0.15f, 0}, {0.10f, 0.26f, 0.10f}, COL_METAL);

        Node* fore = arm->addChild("antebraco" + tag, {0, -UPPER_ARM_LEN, 0});
        fore->part(S::Sphere, {0, 0, 0},       glm::vec3(0.11f),      COL_DARK)
            ->part(S::Cube,   {0, -0.135f, 0}, {0.09f, 0.24f, 0.09f}, COL_METAL);

        Node* hand = fore->addChild("mao" + tag, {0, -FOREARM_LEN, 0});
        hand->part(S::Sphere, {0, 0, 0},      glm::vec3(0.08f),      COL_DARK)
            ->part(S::Cube,   {0, -0.07f, 0}, {0.07f, 0.11f, 0.10f}, COL_DARK);

        // perna, quadril joelho e tornozelo
        Node* thigh = r.pelvis->addChild("coxa" + tag, {sx * HIP_HALF, 0, 0});
        thigh->part(S::Sphere, {0, 0, 0},      glm::vec3(0.15f),      COL_DARK)
             ->part(S::Cube,   {0, -0.22f, 0}, {0.14f, 0.34f, 0.15f}, COL_METAL);

        Node* shin = thigh->addChild("canela" + tag, {0, -THIGH_LEN, 0});
        shin->part(S::Sphere, {0, 0, 0},        glm::vec3(0.13f),      COL_DARK)
            ->part(S::Cube,   {0, 0, 0.065f},   {0.08f, 0.08f, 0.03f}, COL_ACCENT)  // joelheira
            ->part(S::Cube,   {0, -0.23f, 0},   {0.12f, 0.34f, 0.13f}, COL_METAL);

        // pe, a sola fica 8 cm abaixo do tornozelo
        Node* foot = shin->addChild("pe" + tag, {0, -SHIN_LEN, 0});
        foot->part(S::Sphere, {0, 0, 0},            glm::vec3(0.09f),      COL_DARK)
            ->part(S::Cube,   {0, -0.045f, 0.06f},  {0.13f, 0.07f, 0.26f}, COL_ACCENT);

        r.upperArm[side] = arm;
        r.forearm[side] = fore;
        r.hand[side] = hand;
        r.thigh[side] = thigh;
        r.shin[side] = shin;
        r.foot[side] = foot;
    }
    return r;
}

// animacao

// a fase vai de 0 a 1 e equivale a um ciclo completo, dois passos
// na fase 0 o pe encosta no chao e na fase duty ele sai do chao
// a perna esquerda fica meio ciclo defasada da direita
// se o pe fica no chao menos da metade do ciclo tem um momento com os dois pes no ar, isso e correr
struct Gait {
    float freq;         // ciclos por segundo
    float duty;         // fracao do ciclo com o pe no chao
    float stride;       // quanto o quadril anda durante o apoio em metros
    float hipHeight;    // altura media do quadril
    float bob;          // sobe e desce do quadril, positivo andando e negativo correndo
    float footLift;     // altura maxima do pe no balanco
    float liftPeak;     // ponto do balanco onde o pe fica mais alto
    float liftExp;      // formato da curva de subida do pe
    float toePitch;     // inclinacao do pe no balanco em graus
    float shoulderAmp;  // amplitude dos bracos em graus
    float elbowBase;    // dobra minima do cotovelo
    float elbowAmp;     // dobra extra quando o braco vai pra frente
    float torsoLean;    // inclinacao do tronco pra frente
    float torsoTwist;   // torcao do tronco
    float armSpread;    // abertura dos bracos pro lado
    float breath;       // respiracao e olhar pros lados quando ta parado
};

Gait gaitIdle() {
    Gait g{};
    g.freq = 0.0f;   g.duty = 0.60f;  g.stride = 0.0f;    g.hipHeight = 0.976f;
    g.bob = 0.0f;    g.footLift = 0.0f; g.liftPeak = 0.40f; g.liftExp = 1.0f;
    g.toePitch = 0.0f;
    g.shoulderAmp = 0.0f; g.elbowBase = 10.0f; g.elbowAmp = 0.0f;
    g.torsoLean = 0.0f;   g.torsoTwist = 0.0f; g.armSpread = 7.0f; g.breath = 1.0f;
    return g;
}

Gait gaitWalk() {
    Gait g{};
    g.freq = 1.0f;   g.duty = 0.60f;  g.stride = 0.66f;    g.hipHeight = 0.935f;
    g.bob = 0.033f;  g.footLift = 0.11f; g.liftPeak = 0.40f; g.liftExp = 1.0f;
    g.toePitch = 12.0f;
    g.shoulderAmp = 22.0f; g.elbowBase = 15.0f; g.elbowAmp = 15.0f;
    g.torsoLean = 4.0f;    g.torsoTwist = 7.0f; g.armSpread = 5.0f; g.breath = 0.2f;
    return g;
}

Gait gaitRun() {
    Gait g{};
    g.freq = 1.5f;   g.duty = 0.30f;  g.stride = 0.56f;    g.hipHeight = 0.91f;
    g.bob = -0.015f; g.footLift = 0.30f; g.liftPeak = 0.33f; g.liftExp = 1.3f;
    g.toePitch = -12.0f;
    g.shoulderAmp = 40.0f; g.elbowBase = 80.0f; g.elbowAmp = 15.0f;
    g.torsoLean = 12.0f;   g.torsoTwist = 11.0f; g.armSpread = 8.0f; g.breath = 0.0f;
    return g;
}

Gait lerpGait(const Gait& a, const Gait& b, float t) {
    auto L = [t](float x, float y) { return x + (y - x) * t; };
    Gait g;
    g.freq = L(a.freq, b.freq);
    g.duty = L(a.duty, b.duty);
    g.stride = L(a.stride, b.stride);
    g.hipHeight = L(a.hipHeight, b.hipHeight);
    g.bob = L(a.bob, b.bob);
    g.footLift = L(a.footLift, b.footLift);
    g.liftPeak = L(a.liftPeak, b.liftPeak);
    g.liftExp = L(a.liftExp, b.liftExp);
    g.toePitch = L(a.toePitch, b.toePitch);
    g.shoulderAmp = L(a.shoulderAmp, b.shoulderAmp);
    g.elbowBase = L(a.elbowBase, b.elbowBase);
    g.elbowAmp = L(a.elbowAmp, b.elbowAmp);
    g.torsoLean = L(a.torsoLean, b.torsoLean);
    g.torsoTwist = L(a.torsoTwist, b.torsoTwist);
    g.armSpread = L(a.armSpread, b.armSpread);
    g.breath = L(a.breath, b.breath);
    return g;
}

// velocidade pro pe de apoio nao escorregar, o quadril anda stride metros enquanto o pe ta no chao
float gaitSpeed(const Gait& g) { return g.stride * g.freq / g.duty; }

// altura do quadril, oscila uma vez por passo
float gaitHipHeight(const Gait& g, float phase) {
    return g.hipHeight + g.bob * std::cos(4.0f * PI * (phase - 0.5f * g.duty));
}

// curva de hermite com posicoes p0 e p1 e tangentes m0 e m1
float hermite(float p0, float m0, float p1, float m1, float s) {
    float s2 = s * s, s3 = s2 * s;
    return (2 * s3 - 3 * s2 + 1) * p0 + (s3 - 2 * s2 + s) * m0 + (-2 * s3 + 3 * s2) * p1 + (s3 - s2) * m1;
}

// onde o tornozelo tem que estar em cada fase do ciclo
struct FootTarget {
    float z;        // em relacao ao quadril, positivo e pra frente
    float y;        // altura do tornozelo no mundo
    float pitch;    // inclinacao do pe em radianos
    bool stance;    // se o pe ta apoiado no chao
};

FootTarget footTarget(float p, const Gait& g) {
    const float half = 0.5f * g.stride;
    if (p < g.duty) {
        // apoio, o pe fica parado no chao entao em relacao ao quadril ele vai da frente pra tras
        float u = p / g.duty;
        return {half * (1.0f - 2.0f * u), ANKLE_H, 0.0f, true};
    }
    // balanco, o pe volta pra frente fazendo um arco
    float s = (p - g.duty) / (1.0f - g.duty);
    float tangent = -0.6f * g.stride * (1.0f - g.duty) / g.duty;  // continua com a velocidade do apoio
    float z = hermite(-half, tangent, half, tangent, s);
    // arco em forma de seno com o pico no ponto certo do balanco
    float peak = std::clamp(g.liftPeak, 0.05f, 0.95f);
    float w = (s < peak) ? 0.5f * s / peak : 0.5f + 0.5f * (s - peak) / (1.0f - peak);
    float bump = std::max(0.0f, std::sin(PI * w));
    float lift = g.footLift * std::pow(bump, g.liftExp);
    float pitch = glm::radians(g.toePitch) * std::sin(PI * s);
    return {z, ANKLE_H + lift, pitch, false};
}

// cinematica inversa da perna com 2 segmentos, coxa e canela
// recebe a posicao do tornozelo em relacao ao quadril e devolve o angulo da coxa e do joelho
void legIK(float z, float y, float& thighAngle, float& kneeFlex) {
    const float a = THIGH_LEN, b = SHIN_LEN;
    float d = std::clamp(std::sqrt(z * z + y * y), 0.05f, (a + b) * 0.9999f);
    float cosKnee = (a * a + b * b - d * d) / (2.0f * a * b);           // lei dos cossenos
    kneeFlex = PI - std::acos(std::clamp(cosKnee, -1.0f, 1.0f));
    float cosHip = (a * a + d * d - b * b) / (2.0f * a * d);
    thighAngle = std::atan2(z, -y) + std::acos(std::clamp(cosHip, -1.0f, 1.0f));
}

// transforma os parametros da marcha em angulos das articulacoes
// nas pernas e bracos girar negativo em x leva pra frente, no tronco e o contrario
void applyPose(Robot& r, const Gait& g, float phase, float clock, const glm::vec3& pos, float heading) {
    // raiz com posicao, direcao e altura
    float hipY = gaitHipHeight(g, phase);
    r.pelvis->jointOffset = glm::vec3(pos.x, hipY, pos.z);
    r.pelvis->rotation = glm::vec3(0.0f, heading, 0.0f);

    float legPhase[2];
    legPhase[DIR] = phase;
    legPhase[ESQ] = std::fmod(phase + 0.5f, 1.0f);

    // pernas usando cinematica inversa
    for (int side = ESQ; side <= DIR; ++side) {
        FootTarget ft = footTarget(legPhase[side], g);
        float thighA, kneeA;
        legIK(ft.z, ft.y - hipY, thighA, kneeA);
        r.thigh[side]->rotation = glm::vec3(-glm::degrees(thighA), 0.0f, 0.0f);
        r.shin[side]->rotation = glm::vec3(glm::degrees(kneeA), 0.0f, 0.0f);
        // tornozelo desfaz a rotacao da perna pro pe ficar reto
        r.foot[side]->rotation = glm::vec3(glm::degrees(thighA - kneeA - ft.pitch), 0.0f, 0.0f);
    }

    // respiracao e movimentos de quando ta parado
    float breath = std::sin(2.0f * PI * 0.25f * clock);
    float lookAround = std::sin(2.0f * PI * 0.11f * clock);

    // tronco inclina e torce junto com os bracos
    r.torso->rotation = glm::vec3(g.torsoLean + g.breath * 1.5f * breath,
                                  g.torsoTwist * std::cos(2.0f * PI * legPhase[ESQ]),
                                  g.breath * 1.2f * std::sin(2.0f * PI * 0.15f * clock));
    r.neck->rotation = glm::vec3(-0.6f * g.torsoLean - g.breath * 1.0f * breath, 0.0f, 0.0f);
    r.head->rotation = glm::vec3(g.breath * 3.0f * std::sin(2.0f * PI * 0.07f * clock + 1.0f),
                                 g.breath * 18.0f * lookAround, 0.0f);

    // cada braco balanca junto com a perna do outro lado
    for (int side = ESQ; side <= DIR; ++side) {
        const float sx = (side == ESQ) ? 1.0f : -1.0f;
        float c = std::cos(2.0f * PI * legPhase[1 - side]);  // 1 quando o braco ta todo na frente
        float swing = g.shoulderAmp * c - 0.5f * g.torsoLean;
        r.upperArm[side]->rotation = glm::vec3(-swing, 0.0f, sx * (g.armSpread + g.breath * 1.5f * breath));
        r.forearm[side]->rotation = glm::vec3(-(g.elbowBase + g.elbowAmp * 0.5f * (1.0f + c)), 0.0f, 0.0f);
        r.hand[side]->rotation = glm::vec3(-0.15f * g.elbowBase, 0.0f, 0.0f);
    }
}

// estado do programa, camera e entrada

enum class Mode { Parado = 0, Andando = 1, Correndo = 2 };

const char* modeName(Mode m) {
    switch (m) {
        case Mode::Parado: return "Parado";
        case Mode::Andando: return "Andando";
        case Mode::Correndo: return "Correndo";
    }
    return "";
}

Gait gaitFor(Mode m) {
    switch (m) {
        case Mode::Andando: return gaitWalk();
        case Mode::Correndo: return gaitRun();
        default: return gaitIdle();
    }
}

struct Graphics {
    ShaderProgram shader;
    Mesh cube, sphere, plane;
};

struct App {
    GLFWwindow* window = nullptr;
    int fbWidth = 1280, fbHeight = 720;
    Graphics gfx;
    Robot robot;

    // animacao
    Mode mode = Mode::Parado;
    Gait gait = gaitIdle();     // parametros atuais ja interpolados
    float phase = 0.0f;         // fase do ciclo da perna direita
    float clock = 0.0f;         // tempo da animacao em segundos
    glm::vec3 position{0.0f};   // posicao do robo no chao
    float heading = 0.0f;       // direcao em graus
    float speed = 0.0f;         // metros por segundo

    // camera orbital
    float camYaw = 60.0f, camPitch = 14.0f, camDist = 5.5f;
    bool camFollow = true;      // camera gira junto com o robo
    float camHeading = 0.0f;    // direcao suavizada da camera
    glm::vec3 camTarget{0.0f, 1.1f, 0.0f};
    bool dragging = false;
    double lastX = 0.0, lastY = 0.0;

    // opcoes
    bool paused = false, slowMotion = false, wireframe = false, showAxes = false;
    float titleTimer = 0.0f;
} app;

void setMode(Mode m) {
    if (app.mode == m) return;
    app.mode = m;
    std::cout << "Modo: " << modeName(m) << '\n';
    app.titleTimer = 0.0f;  // atualiza o titulo no proximo quadro
}

void resetScene() {
    app.position = glm::vec3(0.0f);
    app.heading = app.camHeading = 0.0f;
    app.camYaw = 60.0f;
    app.camPitch = 14.0f;
    app.camDist = 5.5f;
    app.camTarget = glm::vec3(0.0f, 1.1f, 0.0f);
}

void framebufferSizeCallback(GLFWwindow*, int width, int height) {
    app.fbWidth = width;
    app.fbHeight = height;
}

void keyCallback(GLFWwindow* window, int key, int, int action, int) {
    if (action != GLFW_PRESS) return;
    switch (key) {
        case GLFW_KEY_ESCAPE: glfwSetWindowShouldClose(window, GLFW_TRUE); break;
        case GLFW_KEY_1: case GLFW_KEY_KP_1: setMode(Mode::Parado); break;
        case GLFW_KEY_2: case GLFW_KEY_KP_2: setMode(Mode::Andando); break;
        case GLFW_KEY_3: case GLFW_KEY_KP_3: setMode(Mode::Correndo); break;
        case GLFW_KEY_W: case GLFW_KEY_UP:
            setMode(static_cast<Mode>(std::min(static_cast<int>(app.mode) + 1, 2)));
            break;
        case GLFW_KEY_S: case GLFW_KEY_DOWN:
            setMode(static_cast<Mode>(std::max(static_cast<int>(app.mode) - 1, 0)));
            break;
        case GLFW_KEY_P: case GLFW_KEY_SPACE: app.paused = !app.paused; break;
        case GLFW_KEY_T: app.slowMotion = !app.slowMotion; break;
        case GLFW_KEY_F: app.wireframe = !app.wireframe; break;
        case GLFW_KEY_J: app.showAxes = !app.showAxes; break;
        case GLFW_KEY_C:
            // mantem o enquadramento ao trocar o modo da camera
            app.camYaw += app.camFollow ? app.camHeading : -app.heading;
            app.camHeading = app.heading;
            app.camFollow = !app.camFollow;
            break;
        case GLFW_KEY_R: resetScene(); break;
        default: break;
    }
}

void mouseButtonCallback(GLFWwindow* window, int button, int action, int) {
    if (button == GLFW_MOUSE_BUTTON_LEFT) {
        app.dragging = (action == GLFW_PRESS);
        glfwGetCursorPos(window, &app.lastX, &app.lastY);
    }
}

void cursorPosCallback(GLFWwindow*, double x, double y) {
    if (!app.dragging) return;
    app.camYaw -= static_cast<float>(x - app.lastX) * 0.3f;
    app.camPitch = std::clamp(app.camPitch + static_cast<float>(y - app.lastY) * 0.3f, 2.0f, 85.0f);
    app.lastX = x;
    app.lastY = y;
}

void scrollCallback(GLFWwindow*, double, double yOffset) {
    app.camDist = std::clamp(app.camDist * std::pow(0.9f, static_cast<float>(yOffset)), 2.0f, 25.0f);
}

glm::vec3 cameraEye() {
    float yaw = glm::radians(app.camYaw + (app.camFollow ? app.camHeading : 0.0f));
    float pitch = glm::radians(app.camPitch);
    glm::vec3 dir(std::cos(pitch) * std::sin(yaw), std::sin(pitch), std::cos(pitch) * std::cos(yaw));
    return app.camTarget + app.camDist * dir;
}

// atualizacao e desenho

void update(float realDt) {
    float dt = app.paused ? 0.0f : realDt * (app.slowMotion ? 0.25f : 1.0f);

    // a e d ou as setas giram o robo
    float turn = 0.0f;
    if (glfwGetKey(app.window, GLFW_KEY_A) == GLFW_PRESS || glfwGetKey(app.window, GLFW_KEY_LEFT) == GLFW_PRESS)
        turn += 1.0f;
    if (glfwGetKey(app.window, GLFW_KEY_D) == GLFW_PRESS || glfwGetKey(app.window, GLFW_KEY_RIGHT) == GLFW_PRESS)
        turn -= 1.0f;
    app.heading += turn * 100.0f * dt;

    // transicao suave, os parametros vao se aproximando do modo escolhido
    app.gait = lerpGait(app.gait, gaitFor(app.mode), 1.0f - std::exp(-3.0f * dt));

    // avanca o ciclo e anda pra onde o robo ta olhando
    app.speed = gaitSpeed(app.gait);
    app.phase = std::fmod(app.phase + app.gait.freq * dt, 1.0f);
    app.clock += dt;
    float h = glm::radians(app.heading);
    app.position += app.speed * dt * glm::vec3(std::sin(h), 0.0f, std::cos(h));

    applyPose(app.robot, app.gait, app.phase, app.clock, app.position, app.heading);
    updateTransforms(app.robot.root.get(), glm::mat4(1.0f));

    // camera segue o robo
    float k = 1.0f - std::exp(-5.0f * realDt);
    app.camTarget = glm::mix(app.camTarget, app.position + glm::vec3(0.0f, 1.1f, 0.0f), k);
    app.camHeading += (app.heading - app.camHeading) * (1.0f - std::exp(-2.5f * realDt));

    // titulo da janela com o modo atual
    app.titleTimer -= realDt;
    if (app.titleTimer <= 0.0f && app.window) {
        app.titleTimer = 0.25f;
        char title[160];
        std::snprintf(title, sizeof(title), "Robô Hierárquico — %s  |  %.1f m/s%s%s", modeName(app.mode),
                      app.speed, app.paused ? "  |  PAUSADO" : "", app.slowMotion ? "  |  câmera lenta" : "");
        glfwSetWindowTitle(app.window, title);
    }
}

void setModel(const glm::mat4& model, bool withNormals) {
    const ShaderProgram& sp = app.gfx.shader;
    glUniformMatrix4fv(sp.uModel, 1, GL_FALSE, glm::value_ptr(model));
    glm::mat3 normalMat = withNormals ? glm::mat3(glm::transpose(glm::inverse(model))) : glm::mat3(1.0f);
    glUniformMatrix3fv(sp.uNormalMat, 1, GL_FALSE, glm::value_ptr(normalMat));
}

// desenha o no e depois os filhos, se receber a matriz de sombra desenha so a sombra
void drawNode(const Node* node, const glm::mat4* shadow) {
    const ShaderProgram& sp = app.gfx.shader;
    for (const Part& part : node->parts) {
        glm::mat4 local = glm::scale(glm::translate(glm::mat4(1.0f), part.offset), part.size);
        glm::mat4 model = node->world * local;
        if (shadow) {
            setModel(*shadow * model, false);
        } else {
            setModel(model, true);
            glUniform1i(sp.uMode, part.emissive ? 1 : 0);
            glUniform3fv(sp.uColor, 1, glm::value_ptr(part.color));
        }
        drawMesh(part.shape == Shape::Cube ? app.gfx.cube : app.gfx.sphere);
    }
    for (const auto& child : node->children) drawNode(child.get(), shadow);
}

// mostra os eixos locais de cada articulacao, x vermelho, y verde e z azul
void drawAxes(const Node* node) {
    const ShaderProgram& sp = app.gfx.shader;
    const float len = 0.16f, th = 0.014f;
    const glm::vec3 axes[3] = {{1, 0, 0}, {0, 1, 0}, {0, 0, 1}};
    for (int i = 0; i < 3; ++i) {
        glm::vec3 size = glm::vec3(th) + axes[i] * (len - th);
        glm::mat4 model = node->world * glm::scale(glm::translate(glm::mat4(1.0f), axes[i] * (0.5f * len)), size);
        setModel(model, true);
        glUniform1i(sp.uMode, 1);
        glUniform3fv(sp.uColor, 1, glm::value_ptr(axes[i]));
        drawMesh(app.gfx.cube);
    }
    for (const auto& child : node->children) drawAxes(child.get());
}

void render() {
    const ShaderProgram& sp = app.gfx.shader;
    glViewport(0, 0, app.fbWidth, app.fbHeight);
    glClearColor(COL_SKY.r, COL_SKY.g, COL_SKY.b, 1.0f);
    glClearStencil(0);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);

    float aspect = app.fbHeight > 0 ? static_cast<float>(app.fbWidth) / static_cast<float>(app.fbHeight) : 1.0f;
    glm::mat4 proj = glm::perspective(glm::radians(45.0f), aspect, 0.1f, 300.0f);
    glm::vec3 eye = cameraEye();
    glm::mat4 view = glm::lookAt(eye, app.camTarget, glm::vec3(0, 1, 0));

    glUseProgram(sp.id);
    glUniformMatrix4fv(sp.uProj, 1, GL_FALSE, glm::value_ptr(proj));
    glUniformMatrix4fv(sp.uView, 1, GL_FALSE, glm::value_ptr(view));
    glUniform3fv(sp.uLightDir, 1, glm::value_ptr(LIGHT_DIR));
    glUniform3fv(sp.uCamPos, 1, glm::value_ptr(eye));
    glUniform3fv(sp.uFogColor, 1, glm::value_ptr(COL_SKY));

    // chao grande que acompanha o robo
    glm::mat4 floorModel = glm::translate(glm::mat4(1.0f),
                                          glm::vec3(std::floor(app.position.x), 0.0f, std::floor(app.position.z)));
    floorModel = glm::scale(floorModel, glm::vec3(600.0f, 1.0f, 600.0f));
    setModel(floorModel, true);
    glUniform1i(sp.uMode, 2);
    drawMesh(app.gfx.plane);

    // sombra projetada no chao, o stencil evita escurecer o mesmo pixel duas vezes
    glm::mat4 shadowMat(1.0f);
    shadowMat[1][0] = -LIGHT_DIR.x / LIGHT_DIR.y;
    shadowMat[1][1] = 0.0f;
    shadowMat[1][2] = -LIGHT_DIR.z / LIGHT_DIR.y;
    shadowMat = glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, 0.002f, 0.0f)) * shadowMat;

    glEnable(GL_STENCIL_TEST);
    glStencilFunc(GL_EQUAL, 0, 0xFF);
    glStencilOp(GL_KEEP, GL_KEEP, GL_INCR);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glDepthMask(GL_FALSE);
    glUniform1i(sp.uMode, 3);
    glUniform1f(sp.uAlpha, 0.38f);
    drawNode(app.robot.root.get(), &shadowMat);
    glDepthMask(GL_TRUE);
    glDisable(GL_BLEND);
    glDisable(GL_STENCIL_TEST);

    // robo
    if (app.wireframe) glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
    drawNode(app.robot.root.get(), nullptr);
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);

    // eixos das articulacoes por cima de tudo
    if (app.showAxes) {
        glDisable(GL_DEPTH_TEST);
        drawAxes(app.robot.root.get());
        glEnable(GL_DEPTH_TEST);
    }
}

void initScene() {
    app.gfx.shader = createProgram(VERTEX_SHADER, FRAGMENT_SHADER);
    app.gfx.cube = createCube();
    app.gfx.sphere = createSphere(16, 24);
    app.gfx.plane = createPlane();
    app.robot = buildRobot();

    glEnable(GL_DEPTH_TEST);
    glEnable(GL_MULTISAMPLE);

    applyPose(app.robot, app.gait, app.phase, app.clock, app.position, app.heading);
    updateTransforms(app.robot.root.get(), glm::mat4(1.0f));
}

void cleanupScene() {
    destroyMesh(app.gfx.cube);
    destroyMesh(app.gfx.sphere);
    destroyMesh(app.gfx.plane);
    glDeleteProgram(app.gfx.shader.id);
}

void printControls() {
    std::cout <<
        "==============================================\n"
        "  Robô Hierárquico: controles\n"
        "==============================================\n"
        "  1 / 2 / 3       parado / andar / correr\n"
        "  W / S  (setas)  acelerar / desacelerar\n"
        "  A / D  (setas)  virar para esquerda / direita\n"
        "  Mouse (arrastar) girar a câmera   Scroll: zoom\n"
        "  C               câmera segue a direção do robô (liga/desliga)\n"
        "  P / Espaço      pausar        T  câmera lenta\n"
        "  F               modo aramado  J  eixos das articulações\n"
        "  R               reiniciar posição   ESC  sair\n"
        "==============================================\n";
}

// main

int main() {
    if (!glfwInit()) {
        std::cerr << "Falha ao inicializar GLFW\n";
        return -1;
    }

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_SAMPLES, 4);         // antisserrilhado
    glfwWindowHint(GLFW_STENCIL_BITS, 8);    // usado na sombra

    GLFWwindow* window = glfwCreateWindow(1280, 720, "Robô Hierárquico", nullptr, nullptr);
    if (!window) {
        std::cerr << "Falha ao criar janela GLFW\n";
        glfwTerminate();
        return -1;
    }
    app.window = window;

    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);
    glfwSetFramebufferSizeCallback(window, framebufferSizeCallback);
    glfwSetKeyCallback(window, keyCallback);
    glfwSetMouseButtonCallback(window, mouseButtonCallback);
    glfwSetCursorPosCallback(window, cursorPosCallback);
    glfwSetScrollCallback(window, scrollCallback);
    glfwGetFramebufferSize(window, &app.fbWidth, &app.fbHeight);

    if (!gladLoadGLLoader(reinterpret_cast<GLADloadproc>(glfwGetProcAddress))) {
        std::cerr << "Falha ao inicializar GLAD\n";
        glfwTerminate();
        return -1;
    }

    initScene();
    printControls();

    double last = glfwGetTime();
    while (!glfwWindowShouldClose(window)) {
        double now = glfwGetTime();
        float dt = static_cast<float>(std::min(now - last, 0.1));  // evita salto se a janela travar
        last = now;

        update(dt);
        render();

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    cleanupScene();
    glfwTerminate();
    return 0;
}
